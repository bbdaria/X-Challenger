import openai
from agents import Agent, Runner
import os
import logging

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("uvicorn.error")

class OpenAIAgent:
    def __init__(self, model="gpt-3.5-turbo", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set")
            raise ValueError("OPENAI_API_KEY is not set")
        openai.api_key = self.api_key
        logger.info(f"OpenAIAgent initialized with model: {self.model}")

    async def act(self, input):
        logger.info(f"OpenAIAgent sending prompt: {input}")
        runner = await Runner(self.agent, input)
        result = runner.output
        logger.info(f"OpenAIAgent received response: {result}")
        return result
