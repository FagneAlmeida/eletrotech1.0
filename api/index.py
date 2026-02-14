from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if not firebase_admin._apps:
    # A Vercel lerá o JSON que você colar nas variáveis de ambiente
    cert_json = json.loads(os.environ.get("FIREBASE_SERVICE_ACCOUNT"))
    cred = credentials.Certificate(cert_json)
    firebase_admin.initialize_app(cred)

db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

@app.get("/api/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    docs = db.collection("orcamentos").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    db.collection("orcamentos").add(orc)
    return {"status": "sucesso"}

@app.delete("/api/orcamentos/{id}")
async def excluir(id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    db.collection("orcamentos").document(id).delete()
    return {"status": "ok"}