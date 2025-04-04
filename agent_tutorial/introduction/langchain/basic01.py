from dotenv import load_dotenv
import os


load_dotenv()

from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://github.com/tennessine/corpus/blob/master/%E4%B8%89%E5%9B%BD%E6%BC%94%E4%B9%89.txt")

docs = loader.load()

from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    encode_kwargs={'normalize_embeddings': True}
)

from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(all_splits)

question = "三国演义中，曹操指挥和参加了哪些战争？"

retrieved_docs = vector_store.similarity_search(question, k=3)
docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)


from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
  """
  基于上下文，回答问题，如果上下文中没有相关信息，请反馈“我无法从提供的上下文中找到信息”。
  上下文： {context}
  问题：{question}
  回答： ""
  """
)

from langchain_deepseek import ChatDeepSeek

llm = ChatDeepSeek(
  model="deepseek-reasoner",
  temperature=0.1,
  api_key=os.getenv("DEEPSEEK_API_KEY"),
)

answer = llm.invoke(
  prompt.format(question=question, context=docs_content)
)
print(answer)