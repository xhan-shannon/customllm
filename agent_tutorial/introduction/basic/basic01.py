from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.deepseek import DeepSeek
from dotenv import load_dotenv
import os


load_dotenv()

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-zh",
)

llm = DeepSeek(
  model="deepseek-reasoner",
  temperature=0.1,
  api_key=os.getenv("DEEPSEEK_API_KEY"),
)

documents = SimpleDirectoryReader(
  input_files=["story1.txt"]
).load_data()

index = VectorStoreIndex.from_documents(
  documents,
  embed_model=embed_model,
)

query_engine = index.as_query_engine(llm=llm)  # remove llm parameter since we commented out DeepSeek
print(query_engine.query("曹魏阵营中，在曹操征战南北过程中郭嘉谋士是什么性格特点？请以人物性格五芒图来进行人格分析。"))