from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from agent.agent import OpenAIAgent
from images.classifier import ImageClassifier
import requests
import tempfile
import os
import random

# agent = OpenAIAgent()
image_classifier = ImageClassifier()

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
        classifier = ImageClassifier()
        result = classifier.classify_image(tmp_path)
    finally:
        os.remove(tmp_path)

    # Check static analysis for model info
    model_name = None
    for analysis in result.get("static_analysis", []):
        # Example: look for a model in metadata details (customize as needed)
        if analysis["analyzer"] == "analyze_metadata" and analysis.get("ai_related"):
            model_name = analysis.get("details", "unknown")
        if analysis["analyzer"] == "detect_watermark" and analysis.get("found"):
            model_name = analysis.get("details", "unknown")
    if result["prediction"] == "FAKE":
        if model_name:
            return JSONResponse({"result": "fake", "model": model_name})
        else:
            # Randomly choose a model
            model = random.choice(["flux1.", "stable diffusion"])
            return JSONResponse({"result": "fake", "model": model})
    else:
        return JSONResponse({"result": "real"})


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    load_dotenv()
    main()
