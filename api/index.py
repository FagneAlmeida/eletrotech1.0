import os
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

# --- ENGENHARIA DE CAMINHOS ABSOLUTOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Garante que as pastas existam para evitar erro 404/500
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Montagem de Arquivos Estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# --- INICIALIZAÇÃO BLINDADA DO FIREBASE ---
try:
    cred_path = os.path.join(BASE_DIR, "serviceAccountKey.json")
    if not firebase_admin._apps:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            print("AVISO: serviceAccountKey.json não encontrado na raiz!")
    db = firestore.client()
except Exception as e:
    print(f"Erro Crítico Firebase: {e}")
    db = None

API_KEY_SECRET = "eletrotech2026"

# --- ROTAS PRINCIPAIS ---

@app.get("/")
async def read_root(request: Request):
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_path):
        return JSONResponse(status_code=404, content={"erro": "Arquivo index.html não encontrado na pasta /templates"})
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return JSONResponse(status_code=204, content={})

@app.get("/api/orcamentos")
async def get_orcamentos(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Acesso Negado")
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Banco de dados desconectado"})
    
    docs = db.collection("orcamentos").order_by("cliente_nome").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

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
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.delete("/api/orcamentos/excluir/{doc_id}")
async def excluir_orcamento(doc_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403)
    db.collection("orcamentos").document(doc_id).delete()
    return {"status": "removido"}