from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = FastAPI()

# Liberação de CORS para ambiente Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛡️ Blindagem de Inicialização: Previne Erro 500 por variáveis mal formatadas
try:
    if not firebase_admin._apps:
        # Busca a string do JSON nas variáveis de ambiente da Vercel
        cert_content = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        
        if not cert_content:
            print("❌ ERRO: Variável FIREBASE_SERVICE_ACCOUNT não configurada na Vercel.")
        else:
            # Converte a string em dicionário e inicializa o SDK
            cert_dict = json.loads(cert_content)
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"❌ ERRO CRÍTICO NA INICIALIZAÇÃO DO FIREBASE: {str(e)}")

# Instância do Banco de Dados
db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

@app.get("/api/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    
    try:
        # Busca todos os documentos na coleção 'orcamentos'
        docs = db.collection("orcamentos").stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler banco: {str(e)}")

@app.post("/api/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    
    try:
        # Adiciona o orçamento ao Firestore
        db.collection("orcamentos").add(orc)
        return {"status": "sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar: {str(e)}")

@app.delete("/api/orcamentos/{id}")
async def excluir(id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    
    try:
        # Exclui o documento específico pelo ID
        db.collection("orcamentos").document(id).delete()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {str(e)}")