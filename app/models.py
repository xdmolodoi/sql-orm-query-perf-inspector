from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    books: Mapped[list["Book"]] = relationship(back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), index=True)
    author: Mapped[Author] = relationship(back_populates="books")
