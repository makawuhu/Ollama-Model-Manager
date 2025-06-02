import httpx
import json
import traceback
from bs4 import BeautifulSoup
import re

OLLAMA_BASE_URL = "https://ollama.makawuhu.com"
OLLAMA_LIBRARY_URL = "https://ollama.com/library"

# -------- GPU Suitability Check --------
def is_model_suitable(size_str: str) -> bool:
    try:
        value = float(re.findall(r"[\d.]+", size_str)[0])
        return value <= 7
    except:
        return False

# -------- Scrape Ollama.com Public Library --------
async def scrape_ollama_library(limit: int = 100):
    async with httpx.AsyncClient() as client:
        response = await client.get(OLLAMA_LIBRARY_URL)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("a[href^='/library/']")

    models = []
    seen = set()

    for card in cards:
        if len(models) >= limit:
            break

        href = card["href"]
        name = href.split("/")[-1]
        if name in seen:
            continue
        seen.add(name)

        title_el = card.select_one("h2")
        desc_el = card.select_one("p")
        title = title_el.text.strip() if title_el else name
        desc = desc_el.text.strip() if desc_el else ""

        size = MODEL_PARAM_SIZES.get(name.lower(), "Unknown")
        if size == "Unknown":
            match = re.search(r"(\d+(\.\d+)?)[ ]?B", desc)
            size = f"{match.group(1)}B" if match else "Unknown"

        models.append({
            "name": name,
            "title": title,
            "description": desc,
            "params": size,
            "suitable_for_4070_super": is_model_suitable(size),
            "url": f"https://ollama.com{href}"
        })

    return models

# -------- Enhanced Local Model Listing --------
async def list_models_with_descriptions():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        resp.raise_for_status()
        installed_models = resp.json().get("models", [])

    scraped_models = await scrape_ollama_library(limit=100)
    scraped_lookup = {m["name"].lower(): m for m in scraped_models}

    for model in installed_models:
        base = model["name"].split(":")[0].lower()
        match = scraped_lookup.get(base)
        if match:
            model.update({
                "title": match["title"],
                "description": match["description"],
                "public_url": match["url"],
                "params": match["params"],
                "suitable_for_4070_super": match["suitable_for_4070_super"],
            })

    return {"models": installed_models}

# -------- Model Management --------
async def pull_model(name: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{OLLAMA_BASE_URL}/api/pull", json={"name": name})
            response.raise_for_status()
            return {
                "status": "success",
                "response_text": response.text,
                "model": name
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "message": f"Ollama returned {e.response.status_code}: {e.response.text}",
                "model": name
            }
        except Exception as e:
            print("Exception in pull_model():")
            print(traceback.format_exc())
            return {
                "status": "error",
                "message": f"{type(e).__name__}: {str(e)}",
                "model": name
            }

async def delete_model(name: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method="DELETE",
                url=f"{OLLAMA_BASE_URL}/api/delete",
                headers={"Content-Type": "application/json"},
                content=json.dumps({"name": name})
            )
            response.raise_for_status()
            return {
                "status": "deleted",
                "model": name
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "message": f"Ollama returned {e.response.status_code}: {e.response.text}",
                "model": name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": name
            }

# -------- Known Model Sizes --------
MODEL_PARAM_SIZES = {
    "llama3": "8B",
    "llama2": "7B",
    "mistral": "7B",
    "gemma": "2B",
    "gemma3": "2B",
    "qwen1.5": "7B",
    "qwen3": "7B",
    "deepseek": "13B",
    "deepseek-coder": "7B",
    "deepseek-r1": "13B",
    "devstral": "7B",
    "phi3": "4.2B",
    "openhermes": "7B",
    "zephyr": "7B",
    "codellama": "7B"
