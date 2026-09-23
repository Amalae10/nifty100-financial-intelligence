import time
import logging
import sqlite3

from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import (
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
    health,
)
DB="nifty100.db"
START_TIME=time.time()

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("n100-api")

def get_db():
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row
    return conn

app=FastAPI(
    title="Nifty100 Financial Intelligence API",
    version="1.0.0"
)

API_PREFIX = "/api/v1"

app.include_router(companies.router, prefix=API_PREFIX, tags=["Companies"])
app.include_router(screener.router, prefix=API_PREFIX, tags=["Screener"])
app.include_router(sectors.router, prefix=API_PREFIX, tags=["Sectors"])
app.include_router(peers.router, prefix=API_PREFIX, tags=["Peers"])
app.include_router(valuation.router, prefix=API_PREFIX, tags=["Valuation"])
app.include_router(portfolio.router, prefix=API_PREFIX, tags=["Portfolio"])
app.include_router(documents.router, prefix=API_PREFIX, tags=["Documents"])
app.include_router(health.router, prefix=API_PREFIX, tags=["Health"])

# CORS -internal ues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start

    logger.info(
        "%s %s %.3fs",
        request.method,
        request.url.path,
        duration
    )

    return response

@app.get("/")
def root():
    return {
        "message": "Nifty100 Financial Intelligence API"
    }