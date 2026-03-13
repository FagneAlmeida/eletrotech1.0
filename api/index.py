from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Inicialização Blindada do Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()

# Segurança de Classe Sênior
API_KEY_SECRET = "eletrotech2026"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/orcamentos")
async def get_orcamentos(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Acesso Negado")
    
    docs = db.collection("orcamentos").order_by("cliente_nome").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/orcamentos/salvar")
async def salvar_orcamento(request: Request, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Não autorizado")
    
    try:
        dados = await request.json()
        # O Firestore aceita o dicionário direto, incluindo o novo cliente_telefone
        doc_ref = db.collection("orcamentos").document()
        doc_ref.set(dados)
        return {"status": "sucesso", "id": doc_ref.id}
    except Exception as e:
        # Log de erro para evitar o crash do middleware
        print(f"Erro Crítico no Middleware: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.delete("/api/orcamentos/excluir/{doc_id}")
async def excluir_orcamento(doc_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403)
    db.collection("orcamentos").document(doc_id).delete()
    return {"status": "removido"}