import openai
from agents import Agent, Runner
import os

class OpenAIAgent:
    def __init__(self, model="o4-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    async def act(self, input):
        runner = await Runner(self.agent, input)
        return runner.output
