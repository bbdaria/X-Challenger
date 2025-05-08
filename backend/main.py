from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from agent.agent import OpenAIAgent
from images.classifier import ImageClassifier

agent = OpenAIAgent()
image_classifier = ImageClassifier()

app = FastAPI()

@app.post("/text")
async def read_root(request: Request):
    data = await request.json()
    text = data.get("text")
    response = agent.act(text)
    return JSONResponse({"response": response})

@app.post("/image")
async def read_root(request: Request):
    data = await request.json()
    image_url = data.get("image_url")
    prediction = image_classifier.classify_image(image_url)
    return JSONResponse({"prediction": prediction})


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    load_dotenv()
    main()
