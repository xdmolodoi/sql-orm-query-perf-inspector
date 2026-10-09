from pathlib import Path
from fastapi import FastAPI, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base
from app.inspector import query_store
from app.demo import seed_demo_data, run_healthy, run_n_plus_one, run_slow

app = FastAPI(title="SQL / ORM Query Perf Inspector",
              description="Query history, slow-query monitoring, and heuristic N+1 detection.", version="1.0.0")
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        seed_demo_data(db)
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    html = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/summary")
def summary():
    return query_store.summary()

@app.get("/api/queries")
def queries(limit: int = Query(default=100, ge=1, le=500)):
    return {"items": query_store.events(limit)}


@app.get("/api/alerts")
def alerts():
    return {"items": query_store.alerts()}


@app.post("/api/demo/healthy")
def healthy(db: Session = Depends(get_db)):
    return run_healthy(db)


@app.post("/api/demo/n-plus-one")
def n_plus_one(db: Session = Depends(get_db)):
    return run_n_plus_one(db)


@app.post("/api/demo/slow")
def slow(db: Session = Depends(get_db)):
    return run_slow(db)


@app.post("/api/clear")
def clear():
    query_store.clear()
    return {"status": "cleared"}


@app.post("/api/clear")
def clear():
    query_store.clear()
    return {"status": "cleared"}
