import logging
from os import environ
from dotenv import load_dotenv
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import requests

# Load environment variables
load_dotenv()
OPENAI_API_KEY = environ["OPENAI_API_KEY"]

# Configure logging
logging.basicConfig(level=logging.INFO)

class PRMonitorAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4")
        self.storage_context = self.create_storage_context()

        self.storage_context = self.create_storage_context()
        self.index = self.load_or_create_index()
        query_engine = self.index.as_query_engine(similarity_top_k=3, llm=self.llm)
        query_engine_tools = [QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="user_monitors", description="This tool contains the subjects that users have setup to monitor. Use a plain text query find monitors "))]
        self.agent =  ReActAgent.from_tools(
            tools=query_engine_tools,
            llm=self.llm,
            verbose=True,
            max_turns=10,
        )

    def create_storage_context(self):
        """Create a storage context for the vector database."""
        try:
            return StorageContext.from_defaults(persist_dir="monitor_data")
        except Exception as e:
            index = VectorStoreIndex.from_documents([])  # Start with an empty index
            index.storage_context.persist(persist_dir="monitor_data")
            return index.storage_context
        
    def load_or_create_index(self):
        """Load existing index or create a new one if it doesn't exist."""
        try:
            index = load_index_from_storage(self.storage_context)
            logging.info("Loaded existing index.")
            return index
        except Exception as e:
            logging.warning("No existing index found, creating a new one.")
            return VectorStoreIndex.from_documents(["samsung note 25"])  # Start with an empty index

    def add_monitor_query(self, query):
        """Add a new monitoring query to the vector database."""
        # self.index.insert_documents([query])
    #     self.index.storage_context.persist(persist_dir="monitor_data")
        logging.info(f"Added monitor query: {query}")


    def check_article(self, article_content):
        """Monitor articles from a given API URL."""
        try:
            result = self.agent.chat(f"Look through the user monitors and check if the following article contains any information that negatively impacts the publicity and reputation of the montitors in question: {article_content}. Respond with a json object containing a risk assessment (none, critical) [{{'risk': 'str', 'reason': 'str'}}")
            return result
        except Exception as e:
            logging.error(f"Error while monitoring articles: {e}")

if __name__ == "__main__":
    agent = PRMonitorAgent()

    # Example: Adding a user-defined monitor query
    agent.add_monitor_query("samsung note 25")

    # Example: Monitor articles from a hypothetical API
    agent.check_article("New Samsung Note 25 released with advanced features")

    input("Press Enter to end the program...")
