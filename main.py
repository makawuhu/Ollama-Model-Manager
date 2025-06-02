import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama_client import (
    list_models_with_descriptions as list_models,
    pull_model,
    delete_model,
    scrape_ollama_library
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ModelRequest(BaseModel):
    name: str

# In-memory cache for /available-models
_cached_models = None
_cache_time = 0
CACHE_DURATION = 600  # 10 minutes

@app.get("/models")
async def get_models():
    return await list_models()

@app.post("/models")
async def pull(request: ModelRequest):
    return await pull_model(request.name)

@app.delete("/models/{name}")
async def delete(name: str):
    return await delete_model(name)

@app.get("/available-models")
async def available_models():
    global _cached_models, _cache_time

    now = time.time()
    if _cached_models and (now - _cache_time < CACHE_DURATION):
        logger.info("Serving /available-models from cache")
        return _cached_models

    logger.info("Refreshing /available-models from upstream")
    models = await scrape_ollama_library(limit=5)
    _cached_models = models
    _cache_time = now
    return models
