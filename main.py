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
        logging.info("Storage context created")
        index_loaded = True
    except Exception as e:
        index_loaded = False

    if not index_loaded:
        sample_data = SimpleDirectoryReader(
            input_dir="test_data",
        ).load_data()
    
    