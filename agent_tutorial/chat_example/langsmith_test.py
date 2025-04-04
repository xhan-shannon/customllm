LANGCHAIN_TRACING_V2 = True
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_API_KEY = "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"

from langchain_openai import ChatOpenAI


from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("{flower} 的花语是什么？")

from langchain_openai import OpenAI

model = OpenAI(
  base_url="http://localhost:7869/v1",
  model="deepseek-r1:70b",
  temperature=0,
  api_key="no-need"
)

from langchain.schema.output_parser import StrOutputParser
output_parser = StrOutputParser()

chain = prompt | model | output_parser

# Ensure the prompt is a string
result = chain.invoke({"flower": "rose"})
if isinstance(result, list):
    result = ''.join(result)
print(result)


