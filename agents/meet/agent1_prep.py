import nest_asyncio
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_parse import LlamaParse


nest_asyncio.apply()

llm = Groq(model="llama3-8b-8192")
llm_70b = Groq(model="llama3-70b-8192")

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.llm = llm
Settings.embed_model = embed_model

docs_kendrick = LlamaParse(result_type="text").load_data("./data/kendrick.pdf")
docs_drake = LlamaParse(result_type="text").load_data("./data/drake.pdf")
docs_both = LlamaParse(result_type="text").load_data(
    "./data/drake_kendrick_beef.pdf"
)

response = llm.complete("do you like drake or kendrick better?")

print(response)