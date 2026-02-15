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

@app.get("/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    # Busca e ordena por data decrescente
    docs = db.collection("orcamentos").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    try:
        # Adiciona timestamp do servidor para o histórico
        orc["data_criacao"] = datetime.now().isoformat()
        db.collection("orcamentos").add(orc)
        return {"status": "sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/excluir/{doc_id}")
async def excluir(doc_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    try:
        db.collection("orcamentos").document(doc_id).delete()
        return {"status": "removido"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))