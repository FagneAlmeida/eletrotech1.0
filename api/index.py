from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Inicialização com Proteção de Duplicidade
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"ERRO CRÍTICO FIREBASE: {e}")

db = firestore.client()
app = FastAPI()
API_KEY_SECRET = "eletrotech2026"

@app.get("/api/orcamentos")
async def get_orcamentos(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Acesso Negado")
    try:
        # Busca os documentos ordenados por nome
        docs = db.collection("orcamentos").order_by("cliente_nome").stream()
        lista = [{"id": d.id, **d.to_dict()} for d in docs]
        return lista
    except Exception as e:
        print(f"ERRO AO BUSCAR: {e}")
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
        print(f"ERRO AO SALVAR: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})