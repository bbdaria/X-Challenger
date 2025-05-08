import logging
from logging.handlers import RotatingFileHandler
import sys
import os

# --- Robust Logging Setup ---
log_file = os.path.join(os.path.dirname(__file__), "server.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)
log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = [file_handler, console_handler]
# If you don't see logs, check file permissions and that this runs before any other logging config.
root_logger.info("[Startup] Logging is configured and working!")

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from agent.agent import OpenAIAgent
from images.classifier import Wrapper
from images.static_analyzer import StaticImageAnalyzer
import requests
import tempfile
import random

agent = None
# agent = OpenAIAgent()

app = FastAPI()

@app.post("/text")
async def read_root():
    logging.getLogger(__name__).info("/text endpoint called")
    return JSONResponse({"message": "Hello from FastAPI!"})

@app.post("/image")
async def classify_image(request: Request):
    logger = logging.getLogger(__name__)
    logger.info("/image endpoint called")
    data = await request.json()
    url = data.get("url")
    if not url:
        logger.error("Missing 'url' in request body")
        return JSONResponse({"error": "Missing 'url' in request."}, status_code=400)
    try:
        logger.info(f"Downloading image from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        logger.info(f"Image downloaded to {tmp_path}")
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        return JSONResponse({"error": f"Failed to download image: {e}"}, status_code=400)

    try:
        classifier = Wrapper()
        logger.info(f"Classifying image: {tmp_path}")
        result = classifier.classify_image(tmp_path)
        logger.info(f"Classification result: {result}")
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        result = {"error": str(e)}
    finally:
        os.remove(tmp_path)
        logger.info(f"Temporary file {tmp_path} removed")

    return JSONResponse({"static_analysis": static_analysis_results, "classification": result})

def main():
    logging.getLogger(__name__).info("Starting FastAPI server with Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_config=None)

if __name__ == "__main__":
    load_dotenv()
    main()
