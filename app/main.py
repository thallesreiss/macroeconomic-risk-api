from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

app = FastAPI(
    title="Macroeconomic Risk API",
    description="API REST para consumo de dados do BACEN e previsão de Risco de Crédito.",
    version="1.0.0"
)

DB_NAME = "banco_macro_risco.db"

# ---------------------------------------------------------
# MODELO DE DADOS (Pydantic) - Valida a entrada do usuário
# ---------------------------------------------------------
class CenarioEconomico(BaseModel):
    pct_selic: float
    pct_inflacao: float
    pct_endividamento: float
    selic_lag_1: float
    selic_lag_3: float
    inflacao_lag_1: float

# ---------------------------------------------------------
# ROTAS GET - Consultas
# ---------------------------------------------------------
@app.get("/")
def home():
    return {"mensagem": "Bem-vindo à API de Risco Macroeconômico", "documentacao": "/docs"}

@app.get("/status")
def status_check():
    return {"status": "Online", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/historico")
def obter_historico_economico(limite: int = 12):
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql(f"SELECT * FROM fct_macro_credit_analytics ORDER BY ano_mes DESC LIMIT {limite};", conn)
        conn.close()
        return {"sucesso": True, "total_registros": len(df), "dados": df.to_dict(orient="records")}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

# ---------------------------------------------------------
# ROTA POST - Inteligência Artificial Preditiva
# ---------------------------------------------------------
@app.post("/prever-risco")
def prever_risco_credito(cenario: CenarioEconomico):
    """
    Recebe um cenário econômico hipotético, processa via Machine Learning
    e retorna a projeção de inadimplência e a classificação de risco.
    """
    try:
        # 1. Carrega dados e treina o modelo rapidamente
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql("SELECT * FROM fct_macro_credit_analytics ORDER BY ano_mes;", conn)
        conn.close()
        
        features = ['pct_selic', 'pct_inflacao', 'pct_endividamento', 'selic_lag_1', 'selic_lag_3', 'inflacao_lag_1']
        X = df[features]
        y = df['target_inadimplencia_proximo_mes']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # 2. Formata os dados de entrada
        dados_input = np.array([[
            cenario.pct_selic,
            cenario.pct_inflacao,
            cenario.pct_endividamento,
            cenario.selic_lag_1,
            cenario.selic_lag_3,
            cenario.inflacao_lag_1
        ]])
        
        # 3. Faz a previsão
        predicao = model.predict(dados_input)[0]
        
        # 4. Aplica a Regra de Negócio
        if predicao < 4.0:
            status = "🟢 RISCO BAIXO (NORMAL)"
        elif 4.0 <= predicao < 5.5:
            status = "🟡 RISCO MODERADO (ATENÇÃO)"
        else:
            status = "🔴 RISCO CRÍTICO (ESTRESSE)"
            
        return {
            "sucesso": True,
            "inadimplencia_prevista_pct": round(predicao, 2),
            "status_risco": status,
            "cenario_analisado": cenario.dict()
        }
        
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}