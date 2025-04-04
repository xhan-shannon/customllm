import os

os.environ["OPENAI_API_KEY"] = "sk-Snnr7Q7p7x7CrreTffsTrVeyFrqrgdSJsBZD8BXa2c5pb2Sr"
os.environ["SERPAPI_API_KEY"] = "98d8c08481242f007971d6d768bdb66379866012"

from langchain import hub

prompt = hub.pull("hwchase17/react")
print(prompt)

from langchain_openai import OpenAI

llm = OpenAI(
  base_url="http://localhost:7869/v1",
        api_key="no-need",
        model="deepseek-r1:70b",

)

from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import Tool
search = SerpAPIWrapper()

tools = [
    Tool(
        name="Search",
        description="Search the web for information",
        func=search.run
    )
]

from langchain.agents import create_react_agent

agent = create_react_agent(llm, tools, prompt)
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(
  agent=agent, tools=tools, verbose=True,
  handle_parsing_errors=True
)

result = agent_executor.invoke(
  {"input": "How could I design an agent to work Elasticsearch documents and pandas dataframe ?"}
)

print(result)