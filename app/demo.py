import time
from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload
from app.models import Author, Book

def seed_demo_data(db: Session):
    if db.query(Author).count():
        return
    authors = []
    for i in range(1, 9):
        author = Author(name=f"Author {i}")
        author.books = [Book(title=f"Book {i}-{j}") for j in range(1, (i % 3) + 2)]
        authors.append(author)
    db.add_all(authors)
    db.commit()

def run_healthy(db: Session) -> dict:
    authors = db.scalars(select(Author).options(selectinload(Author.books))).all()
    return {"mode": "healthy", "authors": len(authors), "books": sum(len(a.books) for a in authors),
            "message": "Relationships loaded with eager loading in a small number of queries."}

def run_n_plus_one(db: Session) -> dict:
    authors = db.scalars(select(Author)).all()
    total_books = sum(len(author.books) for author in authors)  # intentionally trigger lazy-load N+1
    return {"mode": "n_plus_one", "authors": len(authors), "books": total_books,
            "message": "Intentional N+1 pattern triggered. Inspect repeated SELECT queries."}

def run_slow(db: Session) -> dict:
    time.sleep(0.15)  # application delay, not a slow SQL statement
    db.execute(text("SELECT 1")).scalar_one()
    return {"mode": "slow_demo", "message": "150 ms application delay completed; SQL timing measures SQL execution only."}
