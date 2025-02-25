from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import uuid

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def load_links():
    try:
        with open("links.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_links(links):
    with open("links.json", "w") as file:
        json.dump(links, file)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten/")
async def shorten_link(request: Request, original_url: str = Form(...)):
    links = load_links()

    short_id = str(uuid.uuid4().hex[:6])

    links[short_id] = original_url
    save_links(links)

    return templates.TemplateResponse("index.html", {"request": request, "short_url": f"/{short_id}"})


@app.get("/{short_id}")
async def redirect_link(short_id: str):
    links = load_links()
    original_url = links.get(short_id)

    if original_url:
        return RedirectResponse(url=original_url)
    else:
        return {"error": "Link not found"}
