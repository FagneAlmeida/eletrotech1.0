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

# 🛡️ Inicialização com Limpeza de Caracteres (Corrige o Erro 500)
if not firebase_admin._apps:
    try:
        # Busca a string bruta da variável de ambiente
        raw_cert = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        
        if not raw_cert:
            print("❌ ERRO: Variável FIREBASE_SERVICE_ACCOUNT não encontrada.")
        else:
            # LIMPEZA INDUSTRIAL: Remove quebras de linha e caracteres de controle invisíveis
            # que costumam aparecer ao copiar/colar do Windows para o navegador.
            clean_cert = "".join(char for char in raw_cert if ord(char) >= 32)
            
            cert_dict = json.loads(clean_cert)
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"❌ ERRO NA CARGA DO JSON: {str(e)}")

# Instância do Banco de Dados
db = firestore.client()
API_KEY_SECRET = "eletrotech2026"

@app.get("/api/orcamentos")
async def listar(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        # Busca documentos no Firestore
        docs = db.collection("orcamentos").stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orcamentos/salvar")
async def salvar(orc: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        # Salva o orçamento no Firestore
        db.collection("orcamentos").add(orc)
        return {"status": "sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/orcamentos/{id}")
async def excluir(id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: 
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        # Deleta o documento pelo ID único do Firestore
        db.collection("orcamentos").document(id).delete()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))