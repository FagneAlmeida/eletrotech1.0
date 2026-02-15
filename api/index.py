from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse # Adicionado FileResponse
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials, firestore
import os, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 1. Blindagem de Estáticos (Garante a Logo e Favicon)
# Certifique-se de que sua logo.jpg e favicon.ico estão na raiz do projeto
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

# 2. Rota Corretiva para o Favicon (Mata o erro 404 do console)
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(os.getcwd(), "favicon.ico")) if os.path.exists("favicon.ico") else None

# --- ROTAS DE API (MANTIDAS) ---
@app.get("/api/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    docs = db.collection("orcamentos").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    db.collection("orcamentos").add(orc)
    return {"status": "sucesso"}

@app.get("/", response_class=HTMLResponse)
async def servir_site():
    path = os.path.join(os.getcwd(), "index.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return f.read()
    return "<h1>Erro: index.html não encontrado</h1>"