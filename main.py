import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


API_ENDPOINT = "https://api.vultr.com/v2/"
API_KEY = os.getenv("VULTR_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def format_response(data, error=None):
    return {"data": data, "error": error}

@app.delete("/delete_cluster/{vke_id}")
async def delete_cluster(vke_id: str):
    response = requests.delete(f"{API_ENDPOINT}kubernetes/clusters/{vke_id}/delete-with-linked-resources", headers=HEADERS)
    if response.status_code == 204:
        return {"message": "Cluster and all related resources deleted successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/list_clusters/")
async def list_clusters():
    endpoint = f"{API_ENDPOINT}kubernetes/clusters"
    response = requests.get(endpoint, headers=HEADERS)
    if response.status_code == 200:
        return format_response(response.json())
    else:
        return format_response(None, response.text)


@app.post("/create_clusters/")
async def create_cluster():
    endpoint = f"{API_ENDPOINT}kubernetes/clusters"
    payload = {
        "region": "lax",
        "label": "my-label",
        "version": "v1.27.2+1",
        "node_pools": [
            {
                "node_quantity": 1,
                "plan": "vc2-4c-8gb",
                "label": "my-label",
                "auto_scaler": True,
                "min_nodes": 1,
                "max_nodes": 5
            }
        ]
    }
    response = requests.post(endpoint, headers=HEADERS, json=payload)
    if response.status_code == 201:
        return {"message": "Successfully created Kubernetes cluster", "data": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)