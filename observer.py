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

from newspaper import Article
# Load environment variables
load_dotenv()
OPENAI_API_KEY = environ["OPENAI_API_KEY"]

# Configure logging
# logging.basicConfig(level=logging.INFO)




def fetch_article_content(url):
    """Fetch and parse article content from a URL using newspaper3k"""
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    logging.info(f"Article title: {article.title}")
    with open("temp_text.txt", "w") as file:
        file.write(article.text)
    return article.text

def getPrompt(article_text: str) -> str:
    return (     
        f" Our users have set up monitors in with the monitors tool. Search the monitors for relevant subject mater and classify the following article based on its potential risk level, considering factors like: "
        f"- The possible negative impact on the company or brand reputation\n"
        f"- Public/customer sentiment or media attention surrounding the issue\n"
        f"- The likelihood of the issue escalating\n"
        f"- The urgency and timeliness required to address the matter\n\n"
        f"Please classify the article as 'high-risk,' 'medium-risk,' or 'low-risk'.\n"
        f".\n"
        f"Here is the article text:\n\n{article_text}\n\n"
        f"Return a valid JSON object of {{'monitors': [...]}} with with the following fields for each relevant monitor:\n"
        f"- 'monitor' (the name of the monitor)\n"
        f"- 'classification' (either 'high-risk', 'medium-risk', or 'low-risk').\n"
        f"- If the article is low-risk, return: {{'message': 'This is a low-risk article.'}}\n"
        f"- If the article is medium-risk or high-risk, include:\n"
        f"  - 'summary' (a brief description of the article)\n"
        f"  - 'reason' (why it was classified as medium-risk or high-risk)\n"
    )



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

    def check_article_url(self, url) -> str:
        """Monitor articles from a given URL."""
        try:
            article_content = fetch_article_content(url)
            prompt = getPrompt(article_content)
            # result = self.agent.chat(message=prompt)
            result = self.agent.chat(
                message=f"Look through the user monitors and check if the following article contains any information that negatively impacts the publicity and reputation of anything mentioned in the monitors tool. Respond with a JSON object containing a risk assessment (none, critical) [{json.dumps({'monitor': 'str', 'risk': 'str', 'reason': 'str'})}]. Article: '{article_content}'"
            )
            print(dir(result))
            return json.dumps(result.response, default=str)  # Ensure serialization
        except Exception as e:
            logging.error(f"Error while monitoring articles: {e}")
            return json.dumps({"error": "error monitoring article"})
        
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
