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

# Inicialização Blindada
if not firebase_admin._apps:
    try:
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if raw_cert:
            # Remove quebras de linha e caracteres invisíveis
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            cert_dict = json.loads(clean_cert)
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
        else:
            print("⚠️ FIREBASE_SERVICE_ACCOUNT não encontrada!")
    except Exception as e:
        print(f"❌ Erro ao inicializar Firebase: {e}")

# Só inicializamos o cliente se o app existir para evitar Crash 500
try:
    db = firestore.client()
except Exception:
    db = None

API_KEY_SECRET = "eletrotech2026"

@app.get("/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    if not db: raise HTTPException(status_code=500, detail="Banco não inicializado")
    docs = db.collection("orcamentos").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    db.collection("orcamentos").add(orc)
    return {"status": "sucesso"}

@app.delete("/orcamentos/{id}")
async def excluir(id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    db.collection("orcamentos").document(id).delete()
    return {"status": "ok"}