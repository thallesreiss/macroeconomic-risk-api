from fastapi import FastAPI
from datetime import datetime

# 1. Cria a instância principal da aplicação (O Servidor)
app = FastAPI(
    title="Macroeconomic Risk API",
    description="API REST para consumo de dados do BACEN e previsão de Risco de Crédito.",
    version="1.0.0"
)

# 2. Rota Raiz (Home) - O cartão de visitas da API
@app.get("/")
def home():
    return {
        "mensagem": "Bem-vindo à API de Risco Macroeconômico",
        "documentacao": "/docs",
        "status": "Operacional"
    }

# 3. Rota de Health Check - Usada por sistemas corporativos para saber se a API não caiu
@app.get("/status")
def status_check():
    return {
        "status": "Online",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "versao": "1.0.0"
    }