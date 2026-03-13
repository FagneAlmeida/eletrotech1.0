from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Inicialização com proteção absoluta
try:
    if not firebase_admin._apps:
        # Tenta carregar o arquivo. Se falhar, o servidor não sobe com erro 500
        cred_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"ERRO DE INFRAESTRUTURA (CONSUMER): {e}")
    db = None

app = FastAPI()
API_KEY_SECRET = "eletrotech2026"

@app.get("/api/orcamentos")
async def get_orcamentos(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403)
    if not db:
        return JSONResponse(status_code=503, content={"error": "Banco de dados offline"})
    
    try:
        docs = db.collection("orcamentos").order_by("cliente_nome").stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/orcamentos/salvar")
async def salvar_orcamento(request: Request, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403)
    try:
        dados = await request.json()
        doc_ref = db.collection("orcamentos").document()
        doc_ref.set(dados)
        return {"status": "sucesso", "id": doc_ref.id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})