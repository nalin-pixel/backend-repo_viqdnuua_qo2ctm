import os
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Product, Project, Testimonial, Lead, BlogPost

app = FastAPI(title="Interior Design Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Interior Design Studio Backend running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Helper to transform Mongo documents
class DocumentOut(BaseModel):
    id: str
    data: dict


def _serialize_docs(docs: List[dict]) -> List[dict]:
    serialized = []
    for d in docs:
        d = dict(d)
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
        serialized.append(d)
    return serialized

# PRODUCTS
@app.get("/api/products")
async def list_products(
    category: Optional[str] = Query(None),
    room_type: Optional[str] = Query(None),
    in_stock: Optional[bool] = Query(None)
):
    filt = {}
    if category:
        filt["category"] = category
    if room_type:
        filt["room_type"] = room_type
    if in_stock is not None:
        filt["in_stock"] = in_stock
    try:
        docs = get_documents("product", filt)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PROJECTS / PORTFOLIO
@app.get("/api/projects")
async def list_projects(style: Optional[str] = Query(None), room: Optional[str] = Query(None)):
    filt = {}
    if style:
        filt["style"] = style
    if room:
        filt["room"] = room
    try:
        docs = get_documents("project", filt)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TESTIMONIALS
@app.get("/api/testimonials")
async def list_testimonials(min_rating: int = Query(1, ge=1, le=5)):
    filt = {"rating": {"$gte": min_rating}}
    try:
        docs = get_documents("testimonial", filt)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# BLOG POSTS
@app.get("/api/blogposts")
async def list_blogposts(published: bool = True, keyword: Optional[str] = Query(None)):
    filt = {"published": published}
    if keyword:
        filt["keywords"] = {"$in": [keyword]}
    try:
        docs = get_documents("blogpost", filt)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# LEADS
@app.post("/api/leads")
async def create_lead(lead: Lead):
    try:
        lead_id = create_document("lead", lead)
        # Optional: HubSpot integration if API key present
        hubspot_key = os.getenv("HUBSPOT_API_KEY")
        if hubspot_key:
            try:
                import requests
                # Simple example to create a contact in HubSpot (v3)
                headers = {"Authorization": f"Bearer {hubspot_key}", "Content-Type": "application/json"}
                payload = {
                    "properties": {
                        "email": lead.email,
                        "firstname": lead.name,
                        "phone": lead.phone or "",
                        "lifecyclestage": "lead",
                        "notes": lead.project_details or ""
                    }
                }
                requests.post("https://api.hubapi.com/crm/v3/objects/contacts", json=payload, headers=headers, timeout=5)
            except Exception:
                pass
        return {"id": lead_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# OPTIONAL: Seed demo content
@app.post("/api/seed-demo")
async def seed_demo(token: Optional[str] = Query(None)):
    if token != os.getenv("SEED_TOKEN", "dev"):
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        # Add a few demo products
        demo_products = [
            Product(title="Modern Lounge Chair", description="Ergonomic lounge chair in walnut finish.", price=799.0, category="furniture", room_type="living room", in_stock=True, tags=["modern", "wood"]),
            Product(title="Marble Pendant Light", description="Minimal pendant for kitchen islands.", price=199.0, category="lighting", room_type="kitchen", in_stock=True, tags=["minimal", "lighting"]),
        ]
        for p in demo_products:
            create_document("product", p)

        demo_testimonials = [
            Testimonial(client_name="Ava Patel", project_type="Full Home", rating=5, quote="They transformed our space beyond expectations!"),
            Testimonial(client_name="Liam Chen", project_type="Kitchen Remodel", rating=5, quote="Professional, timely, and stunning results."),
        ]
        for t in demo_testimonials:
            create_document("testimonial", t)

        demo_projects = [
            Project(title="Skyline Penthouse", style="Modern", room="Living Room", budget_range="$$$", duration_weeks=12, description="A sleek urban living space with panoramic views."),
            Project(title="Cozy Minimal Bedroom", style="Minimalist", room="Bedroom", budget_range="$$", duration_weeks=6, description="Calming tones with functional storage solutions."),
        ]
        for pr in demo_projects:
            create_document("project", pr)

        demo_posts = [
            BlogPost(title="Top 7 Custom Home Interiors Trends", slug="custom-home-interiors-trends", excerpt="Explore the latest in custom home interiors.", content="Long-form content about custom home interiors...", keywords=["custom home interiors", "interior design"], published=True),
        ]
        for b in demo_posts:
            create_document("blogpost", b)

        return {"status": "seeded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
