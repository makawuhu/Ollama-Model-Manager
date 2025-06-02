# Ollama Model Manager

A lightweight FastAPI-based backend that lists and manages models from the [Ollama library](https://ollama.com/library), with local caching and 4070 Super compatibility filtering.

## Features

- `/models`: List models already pulled into Ollama
- `/models` (POST): Pull a new model
- `/models/{name}` (DELETE): Delete a local model
- `/available-models`: Scrapes Ollama library and caches model metadata (title, description, parameter size, URL, 4070 Super compatible)

## Setup

### Requirements
- Python 3.11+
- FastAPI
- httpx
- uvicorn
- Ollama installed and running locally

### Installation
```bash
git clone https://github.com/yourname/ollama-model-manager
cd ollama-model-manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Tech Stack
- FastAPI for API
- httpx for async HTTP calls
- BeautifulSoup4 for scraping
- Python standard logging

## API Reference

### `GET /models`
Returns a list of currently installed models.

### `POST /models`
Pull a model by name. Example:
```json
{
  "name": "gemma3"
}
```

### `DELETE /models/{name}`
Delete a local model.

### `GET /available-models`
Returns a list of models from Ollama.com with metadata:
- name
- title
- description
- params (e.g., 7B)
- suitable_for_4070_super
- url

## Future Plans
- Add frontend for browsing and managing models
- Persistent database for tracking downloads
- GPU compatibility picker

---

MIT License
