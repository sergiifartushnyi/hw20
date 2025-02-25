from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import motor.motor_asyncio
from bson.objectid import ObjectId
from pydantic import BaseModel
import uuid

app = FastAPI()

templates = Jinja2Templates(directory="templates")

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://mongo:27017")
db = client.shortlinks
links_collection = db.links

class Link(BaseModel):
    original_url: str
    short_id: str
    click_count: int = 0

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten/")
async def shorten_link(request: Request, original_url: str = Form(...)):
    short_id = str(uuid.uuid4().hex[:6])

    new_link = Link(original_url=original_url, short_id=short_id)
    await links_collection.insert_one(new_link.dict())

    return templates.TemplateResponse("index.html", {"request": request, "short_url": f"/{short_id}"})

@app.get("/{short_id}")
async def redirect_link(short_id: str):
    link = await links_collection.find_one({"short_id": short_id})

    if link:
        await links_collection.update_one(
            {"_id": link["_id"]},
            {"$inc": {"click_count": 1}}
        )
        return RedirectResponse(url=link["original_url"])
    else:
        return {"error": "Link not found"}

@app.put("/edit/{short_id}")
async def edit_link(short_id: str, new_url: str):
    result = await links_collection.update_one(
        {"short_id": short_id},
        {"$set": {"original_url": new_url}}
    )
    if result.matched_count:
        return {"message": "Link updated successfully"}
    else:
        return {"error": "Link not found"}
