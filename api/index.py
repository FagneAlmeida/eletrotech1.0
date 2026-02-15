from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json

app = FastAPI()

# 1. Configuração de Tráfego (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Inicialização do Firebase
if not firebase_admin._apps:
    try:
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if raw_cert:
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            firebase_admin.initialize_app(credentials.Certificate(json.loads(clean_cert)))
    except Exception as e:
        print(f"❌ Erro Firebase: {e}")

db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

# 3. Servir arquivos estáticos (Logo, Favicon) - DEVE FICAR FORA DAS FUNÇÕES
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    app.mount("/static", StaticFiles(directory="."), name="static")

# --- ROTAS DE API (ALINHADAS COM O SEU FRONTEND) ---

@app.get("/api/orcamentos/listar")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    docs = db.collection("orcamentos").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

# Rota exata que o seu console acusou erro 404
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

# --- ROTA DO SITE ---

# --- ROTA DE LISTAGEM SINCRONIZADA ---

# Removi o "/listar" para casar com a chamada do seu app: GET /api/orcamentos
@app.get("/api/orcamentos")
async def listar_orcamentos(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401)
    
    try:
        # Busca no Firestore ordenada por data
        docs = db.collection("orcamentos").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    except Exception as e:
        print(f"Erro ao listar: {e}")
        raise HTTPException(status_code=500, detail=str(e))