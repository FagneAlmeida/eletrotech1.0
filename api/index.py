from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = FastAPI()

# Configuração de Caminhos Absolutos para evitar o 404
base_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(base_dir, "templates")
static_path = os.path.join(base_dir, "static")

# Montagem de Arquivos Estáticos
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

templates = Jinja2Templates(directory=templates_path)

# Inicialização Firebase
try:
    cred_path = os.path.join(base_dir, "serviceAccountKey.json")
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Erro Firebase: {e}")
    db = None

API_KEY_SECRET = "eletrotech2026"

# ROTA PRINCIPAL (Resolve o 404 da raiz)
@app.get("/")
async def read_root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return JSONResponse(status_code=404, content={"detail": "Arquivo index.html nao encontrado na pasta templates"})

# ROTA DO FAVICON (Limpa o erro do console)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    icon_path = os.path.join(static_path, "favicon.ico")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    return JSONResponse(status_code=204, content={}) # Retorna 'sem conteudo' se não existir

@app.get("/api/orcamentos")
async def get_orcamentos(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=403)
    docs = db.collection("orcamentos").order_by("cliente_nome").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/orcamentos/salvar")
async def salvar_orcamento(request: Request, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET: raise HTTPException(status_code=403)
    dados = await request.json()
    db.collection("orcamentos").document().set(dados)
    return {"status": "sucesso"}