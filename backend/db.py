# SQLAlchemy setup and models for Secret Santa
from fastapi import HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from starlette.requests import Request
from pathlib import Path

db_path = Path(__file__).parent.parent / "secretsanta.db"
DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Example User model (replace with your fields)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    token = Column(String, unique=True, index=True)


class SecretSantaPair(Base):
    __tablename__ = "pairs"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    giver_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    giver = relationship("User", foreign_keys=[giver_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class Gift(Base):
    __tablename__ = "gifts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    links = Column(String, nullable=True)  # Comma-separated links
    year = Column(Integer, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_for_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", foreign_keys=[created_by_id])
    created_for = relationship("User", foreign_keys=[created_for_id])


class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    gift_id = Column(Integer, ForeignKey("gifts.id"))
    user = relationship("User")
    gift = relationship("Gift")


def get_user_by_username(db, username: str):
    return db.query(User).filter(User.name == username).first()


def get_current_db_user(request: Request, db: Session) -> User | None:
    """
    Returns the SQLAlchemy User object for the authenticated user in request.state.user.
    Returns None if not found or not authenticated.
    """
    username = getattr(request.state, "user", None)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return db.query(User).filter_by(username=username).first()
