from os import environ
from dotenv import load_dotenv
import logging


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
    response = agent.chat("Should the IBM pr team be aware of anything immediately!")
    logging.info(f'Response {response}')

    input("Press Enter to end the program...")

