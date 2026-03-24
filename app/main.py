from fastapi import FastAPI, HTTPException, Request
import os
from dotenv import load_dotenv
from app.database import Neo4jService
import requests
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter
from app.models import UserCreate, EntryCreate

#get IP address
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # First IP in the list is the original client
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host
    return ip

#get Prescription Category
def get_rxcui(drug_name):
    url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
    params = {"name": drug_name}

    res = requests.get(url, params=params)
    data = res.json()

    try:
        return data["idGroup"]["rxnormId"][0]
    except:
        return None
    
def get_drug_classes(rxcui):
    url = f"https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json"
    params = {"rxcui": rxcui}

    res = requests.get(url, params=params)
    data = res.json()

    classes = []
    try:
        for item in data["rxclassDrugInfoList"]["rxclassDrugInfo"]:
            classes.append(item["rxclassMinConceptItem"]["className"])
    except:
        pass

    return classes

def get_rxnorm_class_stats(db):
    words = db.get_word_stats()
    class_counts = Counter()
    seen = {}

    for entry in words:
        word = entry["word"]
        count = entry["count"]

        if word in seen:
            classes = seen[word]
        else:
            rxcui = get_rxcui(word)
            classes = get_drug_classes(rxcui) if rxcui else ["Unknown"]
            seen[word] = classes

        for cls in set(classes):
            class_counts[cls] += 1

    data = [
        {"class": k, "count": v}
        for k, v in class_counts.items()
    ]

    data = sorted(data, key=lambda x: x["count"], reverse=True)
    top_n = 6
    top_classes = data[:top_n]
    remaining = data[top_n:]

    # sum remaining into "Other"
    #other_count = sum(item["count"] for item in remaining)

    #if other_count > 0:
        #top_classes.append({"class": "Other", "count": other_count})

    return top_classes


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Neo4jService(os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))


@app.on_event("shutdown")
def shutdown_event():
    db.close()

@app.get("/stats/locations")
def get_location_stats():
    return db.get_location_stats()

@app.get("/stats/words")
def get_word_stats():
    return db.get_word_stats()


@app.get("/stats/categories")
def drug_class_stats():
    return get_rxnorm_class_stats(db)

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

