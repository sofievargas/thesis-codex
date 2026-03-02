from fastapi import FastAPI, HTTPException, Request
import os
from dotenv import load_dotenv
from app.database import Neo4jService
import requests

from app.models import UserCreate, EntryCreate

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # First IP in the list is the original client
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host
    return ip

#use IP address to retrieve region
def geo_lookup(ip: str) -> dict:
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = response.json()

        if data["status"] != "success":
            return {
                "city": "Unknown",
                "region": "Unknown",
                "country": "Unknown"
            }

        return {
            "city": data.get("city", "Unknown"),
            "region": data.get("regionName", "Unknown"),
            "country": data.get("country", "Unknown"),
        }

    except Exception:
        return {
            "city": "Unknown",
            "region": "Unknown",
            "country": "Unknown"
        }

#credentials for Neo4j aura database
load_dotenv()

app = FastAPI(title="Thesis API")


db = Neo4jService(os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))


@app.on_event("shutdown")
def shutdown_event():
    db.close()


@app.post("/users")
def create_user(user: UserCreate):
    node = db.create_user(user.name)
    return {"name": node["name"]}

#1. Check if user exists
#2. Create entry
#3. Draw relationship from user to entry
@app.post("/entries")
def create_entry(entry: EntryCreate, request:Request):
    if not db.user_exists(entry.name):
        raise HTTPException(
            status_code=404,
            detail=f"User '{entry.name}' does not exist"
        )
    client_ip = get_client_ip(request)
    location = geo_lookup(client_ip)
    
    node = db.create_entry(
        location["city"],
        entry.original,
        entry.target,
        entry.word
    )

    #separate ip architecture with geolocation
    #create another 'forwarded' object
    #use ip to get geolocation region and then discard the ip address
    #change neo4j database to store region instead of ip address
    
    """
    Request
    ↓
    Extract IP
    ↓
    Geolocation lookup
    ↓
    Discard IP
    ↓
    Store region only
    ip = get_client_ip(request)
    region = geo_lookup(ip)
    log_event(region=region, metric="translation")
    """
    u, r, e = db.create_relationship(
        location["city"],
        original=entry.original,
        target=entry.target,
        word=entry.word,
        name=entry.name
    )

    return {   
        "user": {
            "id": u.id,
            "labels": list(u.labels),
            "properties": dict(u),
        },
        "relationship": {
            "id": r.id,
            "type": r.type,
            "properties": dict(r),
        },
        "entry": {
            "id": e.id,
            "labels": list(e.labels),
            "properties": dict(e),
        }
    }

@app.get("/nodes")
def get_nodes():
    nodes = db.get_all_nodes()
    return [dict(n) for n in nodes]

