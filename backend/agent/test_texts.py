from agent.agent import OpenAIAgent
import os
import asyncio

fact_checker = OpenAIAgent()

output = asyncio.run(fact_checker.act("am i gay"))

print(output)

