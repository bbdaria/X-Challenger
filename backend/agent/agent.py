import openai
from agents import Agent, Runner
import os

from dotenv import load_dotenv
load_dotenv()

class OpenAIAgent:
    def __init__(self, model="o4-mini", instruction_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "prompt.j2"))):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        # Read instructions from file
        try:
            with open(instruction_file, "r", encoding="utf-8") as f:
                instructions = f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Instruction file '{instruction_file}' not found.")

        self.agent = Agent(name="Assistant", instructions=instructions)

    async def act(self, input):
        runner = await Runner(self.agent, input)
        return runner.output
