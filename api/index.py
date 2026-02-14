from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização com limpeza de caracteres de controle (ASCII < 32)
if not firebase_admin._apps:
    try:
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if not raw_cert:
            print("❌ ERRO: Variável FIREBASE_SERVICE_ACCOUNT não encontrada.")
        else:
            # Remove qualquer caractere de controle invisível (quebras de linha, etc)
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            cert_dict = json.loads(clean_cert)
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"❌ ERRO NA CARGA DO JSON: {str(e)}")

db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

@app.get("/api/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    docs = db.collection("orcamentos").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    db.collection("orcamentos").add(orc)
    return {"status": "sucesso"}

@app.delete("/api/orcamentos/{id}")
async def excluir(id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    db.collection("orcamentos").document(id).delete()
    return {"status": "ok"}