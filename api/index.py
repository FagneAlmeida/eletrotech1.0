from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização Blindada do Firebase
if not firebase_admin._apps:
    try:
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if raw_cert:
            # Limpeza industrial de caracteres de controle
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            cert_dict = json.loads(clean_cert)
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
        else:
            print("⚠️ FIREBASE_SERVICE_ACCOUNT não configurada na Vercel.")
    except Exception as e:
        print(f"❌ ERRO FIREBASE: {str(e)}")

db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

# --- ROTAS INDUSTRIAIS ---

# --- ROTAS CORRIGIDAS E BLINDADAS ---

@app.get("/orcamentos")  # A Vercel entrega como /api/orcamentos
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Chave Inválida")
    if not db: 
        raise HTTPException(status_code=500, detail="Erro de conexão com Banco")
    
    # Busca ordenando por data para o histórico funcionar
    docs = db.collection("orcamentos").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/salvar")  # A Vercel entrega como /api/salvar
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401)
    try:
        # Garante que o histórico tenha uma data para ordenação
        orc["data_criacao"] = datetime.now().isoformat()
        db.collection("orcamentos").add(orc)
        return {"status": "sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/excluir/{doc_id}")  # A Vercel entrega como /api/excluir/ID
async def excluir(doc_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401)
    db.collection("orcamentos").document(doc_id).delete()
    return {"status": "removido"}