import os
from openai import OpenAI
from pydantic import BaseModel


class CalendarEvent(BaseModel):
    title: str
    date: str
    participants: list[str]



client = OpenAI(
  base_url="http://localhost:7869/v1",
  api_key="no-need"
)

completion = client.beta.chat.completions.parse(
    model="deepseek-r1:70b",
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "I have a meeting with John and Jane on 2025-01-01 at 10:00 AM."}
    ],
    response_format=CalendarEvent,
    temperature=0,
)

# print(completion)
event = completion.choices[0].message.parsed
print(event)
