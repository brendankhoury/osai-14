import logging
import json
from os import environ
from dotenv import load_dotenv
from llama_index.core import (
    Document,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import requests
import json
# Load environment variables
load_dotenv()
OPENAI_API_KEY = environ["OPENAI_API_KEY"]

# Configure logging
logging.basicConfig(level=logging.INFO)

class PRMonitorAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4")
        self.index = self.load_index()
        query_engine = self.index.as_query_engine(similarity_top_k=3, llm=self.llm)
        query_engine_tools = [QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="user_monitors", description=("This tool contains the subjects that users have setup to monitor. "                 "Use a detailed plain text question as input to the tool.")
))]
        self.agent =  ReActAgent.from_tools(
            tools=query_engine_tools,
            llm=self.llm,
            verbose=True,
            max_turns=10,
        )

    def load_index(self):
        """Load documents from the monitors directory and create a new index."""
        reader = SimpleDirectoryReader(input_dir="monitors")
        documents = reader.load_data()
        return VectorStoreIndex.from_documents(documents)

    def check_article(self, article_content):
        """Monitor articles from a given API URL."""
        try:
            result = self.agent.chat(
                message=f"Look through the user monitors and check if the following article contains any information that negatively impacts the publicity and reputation of anything mentioned in the monitors tool. Respond with a JSON object containing a risk assessment (none, critical) [{json.dumps({'monitor': 'str', 'risk': 'str', 'reason': 'str'})}]. Article: '{article_content}'"
            )
            return json.dumps(result, default=str)  # Ensure serialization
        except Exception as e:
            logging.error(f"Error while monitoring articles: {e}")
            return json.dumps({"error": str(e)})

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
