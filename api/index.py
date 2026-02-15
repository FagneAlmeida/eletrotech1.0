from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json

app = FastAPI()

# Liberação de tráfego para o seu Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização Robusta do Firebase (Railway detecta variáveis de ambiente nativamente)
if not firebase_admin._apps:
    try:
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if raw_cert:
            # Limpeza de caracteres invisíveis para evitar erro 500
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            cert_dict = json.loads(clean_cert)
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"❌ Falha no Firebase: {str(e)}")

db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

# --- ROTAS DE PRODUÇÃO (Caminho: /api/...) ---

@app.get("/api/orcamentos")
async def listar_orcamentos(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Acesso negado")
    
    # Busca e ordena os orçamentos no Firebase
    docs = db.collection("orcamentos").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/salvar")
async def salvar_orcamento(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401)
    try:
        orc["data_criacao"] = datetime.now().isoformat()
        db.collection("orcamentos").add(orc)
        return {"status": "sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/excluir/{doc_id}")
async def deletar_orcamento(doc_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401)
    db.collection("orcamentos").document(doc_id).delete()
    return {"status": "removido"}
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def servir_site():
    try:
        # Busca o index.html que está na raiz (um nível acima da pasta /api)
        path = os.path.join(os.getcwd(), "index.html")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Erro ao carregar site: {e}</h1>"