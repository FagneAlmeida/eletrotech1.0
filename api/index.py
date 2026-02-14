from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os, json

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Inicialização do Firebase (Mantendo sua lógica de limpeza)
if not firebase_admin._apps:
    try:
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if raw_cert:
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            cert_dict = json.loads(clean_cert)
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
        else:
            print("⚠️ FIREBASE_SERVICE_ACCOUNT não encontrada!")
    except Exception as e:
        print(f"❌ Erro Firebase: {e}")

try:
    db = firestore.client()
except:
    db = None

API_KEY_SECRET = "eletrotech2026"

# --- ROTA QUE SERVE O SEU SITE ---
@app.get("/", response_class=HTMLResponse)
async def servir_site():
    try:
        # Busca o index.html que está na raiz do projeto
        path = os.path.join(os.getcwd(), "index.html")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Erro ao carregar site: {e}</h1>"

# --- ROTAS DA API ---
@app.get("/api/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    if not db: raise HTTPException(status_code=500)
    docs = db.collection("orcamentos").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=401)
    db.collection("orcamentos").add(orc)
    return {"status": "sucesso"}