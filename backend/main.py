from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from agent.agent import OpenAIAgent
from images.classifier import Wrapper
import requests
import tempfile
import os
import random

agent = None
# agent = OpenAIAgent()

app = FastAPI()

@app.post("/text")
async def read_root(request: Request):
    data = await request.json()
    text = data.get("text")
    response = agent.act(text)
    return JSONResponse({"response": response})

@app.post("/image")
async def classify_image(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return JSONResponse({"error": "Missing 'url' in request."}, status_code=400)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
    except Exception as e:
        return JSONResponse({"error": f"Failed to download image: {e}"}, status_code=400)

    try:
        classifier = Wrapper()
        result = classifier.classify_image(tmp_path)
    finally:
        os.remove(tmp_path)

    return JSONResponse(result)


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    load_dotenv()
    main()
