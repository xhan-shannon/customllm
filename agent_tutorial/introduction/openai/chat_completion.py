import os
from openai import OpenAI

client = OpenAI(
  base_url="http://localhost:7869/v1",
  api_key="no-need"
)

response = client.chat.completions.create(
    model="deepseek-r1:70b",
    messages=[{"role": "user", "content": "Hello, world!"}],
    temperature=0.5,
    max_tokens=1000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    stream=False,
)

# Extract and print just the response content
if response.choices:
    assistant_message = response.choices[0].message.content
    print("Assistant:", assistant_message)
else:
    print("No response generated")
