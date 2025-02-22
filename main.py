from os import environ
from dotenv import load_dotenv
import nltk
# nltk.download('punkt')
# nltk.download('punkt_tab')
from newspaper import Article
import logging
import json 


load_dotenv()

OPENAI_API_KEY = environ["OPENAI_API_KEY"]

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

logging.basicConfig(level=logging.INFO)

def fetch_article_content(url):
    """Fetch and parse article content from a URL using newspaper3k"""
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article.text

if __name__ == "__main__":

    llm = OpenAI(model="gpt-4")

    import phoenix as px
    session = px.launch_app()

    from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
    from phoenix.otel import register

    tracer_provider = register()
    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

    # Create a storage context
    
    try: 
        storage_context = StorageContext.from_defaults(
            persist_dir="test_data"
        )
        news_index = load_index_from_storage(storage_context)
    
        logging.info("Storage context created")
        index_loaded = True
    except Exception as e:
        index_loaded = False
    # index_loaded = False
    if not index_loaded:
        news_index = SimpleDirectoryReader(
            input_dir="pdfs",
        ).load_data()
    
        news_index = VectorStoreIndex.from_documents(news_index)
        news_index.storage_context.persist(persist_dir="test_data")

    news_engine = news_index.as_query_engine(similarity_top_k=3,llm=llm)
    
    # Create a query engine tool

    query_engine_tools = [
        QueryEngineTool(
            query_engine=news_engine,
            metadata=ToolMetadata(
                name="news_query_engine",
                description="A query engine for news articles",
            ),
        )
    ]

    agent = ReActAgent.from_tools(
        query_engine_tools,
        llm=llm,
        verbose=True,
        max_turns=10,
    )

    user_query = input("Enter your website article link: ")  
    
    article_text = fetch_article_content(user_query)


    response = agent.chat(
    f"Classify if this article is high-risk or low-risk based on the following criteria of a high-risk article: "
    f"- Potential Negative impact on the company or brand reputation\n"
    f"- Public(customer) sentiment or media attention around the issue\n"
    f"- Whether the issue is likely to escalate\n"
    f"- How urgent/timely the matter needs to be resolved\n\n"
    f"If necessary, you can receive context from other existing articles in our files.\n"
    f"Here is the article text:\n\n{article_text}\n\n"
    f"Return ONLY a valid JSON list where each object has: "
    f"'classification' (state if this article is high risk or low risk). "
    f"If it is not a High-Risk article, return a JSON object stating: {{'message': 'This is not a high-risk article, it is low-risk.'}} Stop there if it is low-risk. "
    f"If it is high risk: 'summary' (brief article description), "
    f"If it is high risk: 'reason' (why it was classified as High-Risk)."   
    )

    response_text = response.response 

    try:
        json_response = json.loads(response_text)
        if isinstance(json_response, list) and json_response:
            logging.info("High-Risk Articles Found")
            print(json.dumps(json_response, indent=4))
        else:
            print(json.dumps({"message": "Nothing high-risk so far."}, indent=4))
    except json.JSONDecodeError:
        logging.error("Failed to parse AI response as JSON.")

    input("Press Enter to end the program...")

