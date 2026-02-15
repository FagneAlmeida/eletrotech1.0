from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Montagem de arquivos estáticos para Logo e Favicon
app.mount("/static", StaticFiles(directory="."), name="static")

if not firebase_admin._apps:
    try:
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if raw_cert:
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            firebase_admin.initialize_app(credentials.Certificate(json.loads(clean_cert)))
    except Exception: pass

db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

@app.get("/api/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    docs = db.collection("orcamentos").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    orc["data_criacao"] = datetime.now().isoformat()
    db.collection("orcamentos").add(orc)
    return {"status": "sucesso"}

@app.delete("/api/orcamentos/excluir/{doc_id}")
async def excluir(doc_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    db.collection("orcamentos").document(doc_id).delete()
    return {"status": "removido"}

@app.get("/", response_class=HTMLResponse)
async def servir_site():
    for p in ["index.html", "../index.html"]:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f: return f.read()
    return "<h1>Sistema EletroTech Online</h1>"