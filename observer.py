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
        query_engine_tools = [QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="user_monitors", description="This tool contains the subjects that users have setup to monitor. Search this tool using the subject of an article to check if a user has set one up."))]
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
            documents = [
                "samsung note 25",
                "iphone 13",
                "google pixel 6",
                "oneplus 9",
                "xiaomi mi 11"
            ]
            return VectorStoreIndex.from_documents(documents)  # Start with an index containing initial documents



    def check_article(self, article_content):
        """Monitor articles from a given API URL."""
        try:
            result = self.agent.chat(message=f"Look through the user monitors and check if the following article contains any information that negatively impacts the publicity and reputation of anything mentioned in the monitors tool: . Respond with a json object containing a risk assessment (none, critical) [{{'monitor': 'str', 'risk': 'str', 'reason': 'str'}}. Article: '{article_content}'")
            return result
        except Exception as e:
            logging.error(f"Error while monitoring articles: {e}")

if __name__ == "__main__":

    import phoenix as px
    session = px.launch_app()

    from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
    from phoenix.otel import register

    tracer_provider = register()
    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

    agent = PRMonitorAgent()

    # Example: Monitor articles from a hypothetical API
    agent.check_article("New Samsung Note 25 released with advanced features")

    input("Press Enter to end the program...")
