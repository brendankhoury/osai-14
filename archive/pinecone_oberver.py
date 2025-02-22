import logging
import json
from os import environ
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = environ["OPENAI_API_KEY"]
PINECONE_API_KEY = environ["PINECONE"]

# Configure logging
logging.basicConfig(level=logging.INFO)

class PRMonitorAgent:
    def __init__(self):
        # Initialize Pinecone
        Pinecone.init(api_key=PINECONE_API_KEY, environment="us-west1-gcp")
        index_name = "monitor-database"
        if index_name not in Pinecone.list_indexes():
            # Create the index if it doesn't exist.
            # (Ensure you use the same dimension as used for your embeddings, e.g., 1536 for text-embedding-ada-002.)
            Pinecone.create_index(index_name, dimension=1536)
        self.pinecone_index = Pinecone.Index(index_name)

        # Initialize LLM
        self.llm = OpenAI(model="gpt-4")

        # Create a query tool that uses Pinecone directly.
        # The tool’s query_engine simply calls our custom query method.
        query_tool = QueryEngineTool(
            query_engine=self,
            metadata=ToolMetadata(
                name="user_monitors",
                description="This tool contains the subjects that users have set up to monitor. "
                            "Query it to find monitors from the Pinecone database."
            )
        )

        # Build the agent using our tool.
        self.agent = ReActAgent.from_tools(
            tools=[query_tool],
            llm=self.llm,
            verbose=True,
            max_turns=10,
        )

    def query(self, query_text: str):
        """
        Query the Pinecone monitor index directly.
        Here we assume that your Pinecone index is pre-populated with monitor entries (for example, "samsung note 25", etc.).
        This function should perform a similarity search using the provided query_text.
        """
        # For demonstration, we assume that the LLM can produce an embedding from the query_text.
        # In a production setting, you would use your embedding model to convert query_text to an embedding vector.
        # Here we simply pass the raw text query to Pinecone.
        try:
            query_response = self.pinecone_index.query(
                query=query_text,
                top_k=3,
                include_metadata=True
            )
            # Format and return the query results.
            return query_response
        except Exception as e:
            logging.error(f"Error querying Pinecone index: {e}")
            return {"error": str(e)}

    def check_article(self, article_content: str):
        """
        Use the agent to check if the provided article contains any information that negatively
        impacts the publicity and reputation of any items in the monitors (stored in Pinecone).
        The agent uses the tool (which in turn calls our .query() method) to answer the question.
        """
        try:
            prompt = (
                "Look through the user monitors (stored in the Pinecone index) and check if the following article "
                "contains any information that negatively impacts the publicity and reputation of anything mentioned "
                "in the monitors. Respond with a JSON object containing a risk assessment (none, critical) in the format "
                "[{'monitor': 'str', 'risk': 'str', 'reason': 'str'}]. "
                f"Article: '{article_content}'"
            )
            result = self.agent.chat(message=prompt)
            return json.dumps(result, default=str)
        except Exception as e:
            logging.error(f"Error while monitoring article: {e}")
            return json.dumps({"error": str(e)})

if __name__ == "__main__":
    agent = PRMonitorAgent()

    # Example: Check an article against the monitors stored in Pinecone.
    output = agent.check_article("New Samsung Note 25 released with advanced features")
    print("Monitor Check Output:", output)

    input("Press Enter to end the program...")
