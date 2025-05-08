from agent.agent import OpenAIAgent
import os

fact_checker = OpenAIAgent()

output = fact_checker.act("am i gay")

print(output)

