import logging
import json
from os import environ
from dotenv import load_dotenv

# llama_index imports
from llama_index import StorageContext
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from llama_index.core.schema import Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import requests

# Load environment variables
load_dotenv()
OPENAI_API_KEY = environ.get("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

class PRMonitorAgent:
    def __init__(self):
        # Initialize the language model
        self.llm = OpenAI(model="gpt-4")

        # Create an in-memory FAISS-based vector store (no persistence)
        vector_store = FAISSVectorStore()
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store
        )

        # Create a brand-new ephemeral index with some initial documents
        self.index = self.create_index_with_initial_docs()

        # Create a query engine from the index
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            llm=self.llm
        )

        # Create a tool for searching monitors in the vector database
        query_engine_tool = QueryEngineTool(
            query_engine=self.query_engine,
            metadata=ToolMetadata(
                name="monitor_search",
                description="Tool to search user-defined monitors stored in the local FAISS DB. Input: plain text query. Output: relevant monitors."  
            )
        )

        # Initialize a ReAct agent with the tool
        self.agent = ReActAgent.from_tools(
            tools=[query_engine_tool],
            llm=self.llm,
            verbose=True,
            max_turns=10
        )

    def create_index_with_initial_docs(self) -> VectorStoreIndex:
        """Builds an in-memory FAISS index with some initial monitors."""
        initial_docs = [
            Document(text="samsung note 25"),
            Document(text="iphone 13"),
            Document(text="google pixel 6"),
            Document(text="oneplus 9"),
            Document(text="xiaomi mi 11"),
        ]
        index = VectorStoreIndex.from_documents(
            documents=initial_docs,
            storage_context=self.storage_context
        )
        logging.info("Created a new ephemeral index with initial monitors.")
        return index

    def add_monitor_query(self, query: str):
        """Add a new monitor to the in-memory FAISS vector database."""
        doc = Document(text=query)
        self.index.insert_documents([doc])
        logging.info(f"Added new monitor: {query}")

    def check_article(self, article_content: str) -> str:
        """Check an article for negative impact on the stored monitors."""
        try:
            # Step 1: Use the agent to gather relevant monitors
            search_prompt = (
                "Use the monitor_search tool to find any monitors that might relate "
                f"to this article:\nArticle: {article_content}\n"
            )
            search_response = self.agent.chat(search_prompt)
            logging.info(f"Relevant monitors found: {search_response}")

            # Step 2: Analyze the article for negative publicity of these monitors
            analysis_prompt = (
                f"Given the following monitors: {search_response}, "
                "analyze the article for negative impact and return a JSON with 'monitor', 'risk' (none, critical), "
                f"and 'reason'. Article: {article_content}"
            )
            result = self.agent.chat(analysis_prompt)

            # Step 3: Return structured JSON
            return json.dumps({
                "relevant_monitors": search_response,
                "analysis": result
            }, default=str)

        except Exception as e:
            logging.error(f"Error while monitoring articles: {e}")
            return json.dumps({"error": str(e)})

if __name__ == "__main__":
    agent = PRMonitorAgent()

    # Example usage:
    # 1) Add a new user-defined monitor
    agent.add_monitor_query("tesla model s")

    # 2) Check an article
    article = "New Samsung Note 25 recall due to battery issues."
    result = agent.check_article(article)
    print("\n===== Analysis Result =====")
    print(result)

    input("\nPress Enter to end the program...\n")
