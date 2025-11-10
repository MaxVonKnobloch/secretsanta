# FastAPI endpoints for Secret Santa
import datetime
import logging
import random

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from backend import config
from backend.auth import token_cookie_guard
from backend.db import get_db, User, SecretSantaPair, Gift, Vote
from backend.gifts import get_receiver, get_gift_list, GiftOut, UserGiftList, get_own_gift_list, add_or_update_gift
from pydantic import BaseModel
from typing import List

app = FastAPI()

# set loglevel to info
logging.basicConfig(level=logging.INFO)

origins = [
    "http://localhost:3000",
    "https://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add static for static/preview
app.mount("/static", StaticFiles(directory=str(config.static.absolute())), name="static")


@app.middleware("http")
async def middleware_wrapper(request: Request, call_next):
    return await token_cookie_guard(request, call_next, admin_only=True, protected_route_prefixes=None)


@app.get("/api/healthcheck")
def read_root():
    return {"message": "Welcome to Secret Santa API"}


@app.get("/api/auth")
def check_auth(request: Request, db: Session = Depends(get_db)):
    try:
        user = get_current_db_user(request, db)
    except HTTPException as exc:
        # ensure frontend receives a JSON object with a success flag and message
        return JSONResponse(status_code=exc.status_code, content={"success": False, "message": str(exc.detail)})
    logging.info(f"Authenticated user: {user.name}")
    return JSONResponse(content={"success": True, "username": user.name})


def get_current_db_user(request: Request, db: Session) -> User:
    """
    Returns the SQLAlchemy User object for the authenticated user in request.state.user.
    Raises HTTPException(401) if not found or not authenticated.
    """
    username = getattr(request.state, "user", None)
    if not username:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user = db.query(User).filter_by(name=username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found in database")
    return user


@app.get("/api/welcome", response_class=HTMLResponse)
async def welcome(request: Request, db: Session = Depends(get_db)):
    user_obj = get_current_db_user(request, db)
    username = user_obj.name
    return f"<h1>Welcome to Secret Santa, {username}!</h1><p>This is the home page.</p>"


@app.get("/api/users", response_model=List[str])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [u.name for u in users]


@app.get("/api/gift-lists", response_model=List[UserGiftList])
def get_gift_lists_for_current_year(request: Request, db: Session = Depends(get_db)):
    user = get_current_db_user(request, db)
    logging.info(f"Fetching gift lists for user: {user.name}")
    current_year = datetime.datetime.now().year

    receiver = get_receiver(user, db, current_year)
    gift_receiver_name = receiver.name if receiver else "?"

    result = [get_own_gift_list(user, db, current_year)]

    # get all users except admin
    other_users = db.query(User).filter(User.name != "admin").all()
    for other_user in sorted(other_users, key=lambda u: u.name):
        gift_list = get_gift_list(other_user, db, current_year)

        if other_user.name == user.name:
            continue
        if other_user.name == gift_receiver_name:
            result.insert(0, gift_list)
        else:
            result.append(gift_list)
    return result


# --- Slogan endpoint ---
@app.get("/api/slogan")
def get_card_slogan():
    slogans = [
        "Deine Schnee-Schnuppe",
        "Deine Lametta-Legende",
        "Dein Rentier-Rockstar",
        "Dein Glühwein-Guru",
        "Dein Keks-König",
        "Dein Zuckerstangen-Zauberer",
        "Dein Frostbeulen-Fürst",
        "Dein Tannenbaum-Tornado",
        "Dein Plätzchen-Panther",
        "Dein Kranz-Kaptiän"
    ]
    return {"slogan": random.choice(slogans)}


# --- Get gift receiver for current user ---
@app.get("/api/receiver")
def get_gift_receiver(request: Request, db: Session = Depends(get_db)):
    logging.info("/receiver endpoint called")
    user_obj = get_current_db_user(request, db)
    current_year = datetime.datetime.now().year
    logging.info(f"Current user: {getattr(user_obj, 'name', None)}, current year: {current_year}")
    pairs = db.query(SecretSantaPair).filter_by(giver_id=user_obj.id, year=current_year).all()
    logging.info(f"Found {len(pairs)} pairs with users: {[(pair.giver_id, pair.receiver_id, pair.year) for pair in pairs]}")

    if pairs:
        pair = pairs[0]
        receiver = db.query(User).filter_by(id=pair.receiver_id).first()
        logging.info(f"Receiver found: {getattr(receiver, 'name', None)}")
        return {"gift_receiver_name": receiver.name}
    logging.info("No receiver found, returning '?'")
    return {"gift_receiver_name": "?"}


class GiftCreate(BaseModel):
    created_for: str  # username instead of id
    title: str
    description: str = ""
    link: str = ""


@app.post("/api/gifts/add", response_model=GiftOut)
def add_gift(gift: GiftCreate, request: Request, db: Session = Depends(get_db)):
    user_obj = get_current_db_user(request, db)
    created_for_user = db.query(User).filter_by(name=gift.created_for).first()
    if not created_for_user:
        raise HTTPException(status_code=404, detail="User not found")

    return add_or_update_gift(
        db=db,
        title=gift.title,
        created_by=user_obj,
        created_for=created_for_user,
        link=gift.link
    )


class GiftUpdate(BaseModel):
    title: str
    link: str


@app.patch("/api/gifts/{gift_id}", response_model=GiftOut)
def update_gift(gift_id: int, update: GiftUpdate, request: Request, db: Session = Depends(get_db)):
    user_obj = get_current_db_user(request, db)
    gift = db.query(Gift).filter_by(id=gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    if gift.created_by != user_obj:
        raise HTTPException(status_code=403, detail="Not allowed")

    return add_or_update_gift(
        db=db,
        gift_pk=gift_id,
        title=update.title,
        created_by=gift.created_by,
        created_for=gift.created_for,
        link=update.link
    )


@app.delete("/api/gifts/{gift_id}")
def delete_gift(gift_id: int, request: Request, db: Session = Depends(get_db)):
    user_obj = get_current_db_user(request, db)
    gift = db.query(Gift).filter_by(id=gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    if gift.created_by != user_obj:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(gift)
    db.commit()
    return {"success": True}


class VoteRequest(BaseModel):
    vote_type: str


@app.post("/api/gifts/{gift_id}/vote")
def vote_gift(gift_id: int, vote: VoteRequest, request: Request, db: Session = Depends(get_db)):
    user_obj = get_current_db_user(request, db)
    gift = db.query(Gift).filter_by(id=gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    vote_value = 1 if vote.vote_type == "up" else -1
    current_vote = db.query(Vote).filter_by(gift=gift, user=user_obj).first()
    if current_vote:
        if current_vote.value == vote_value:
            db.delete(current_vote)
            db.commit()
            user_vote = "inactive"
        else:
            current_vote.value = vote_value
            db.commit()
            user_vote = "up" if vote_value == 1 else "down"
    else:
        new_vote = Vote(gift=gift, user=user_obj, value=vote_value)
        db.add(new_vote)
        db.commit()
        user_vote = "up" if vote_value == 1 else "down"
    # Update vote count (sum all votes for this gift)
    total_votes = db.query(Vote).filter_by(gift=gift).with_entities(Vote.value).all()
    vote_count = sum(v[0] for v in total_votes)
    return {"success": True, "vote_count": vote_count, "user_vote": user_vote}


@app.get("/api/pairing")
def show_current_pairing(request: Request, db: Session = Depends(get_db)):
    """
    Show the current pairing for all users.
    :param request:
    :param db:
    :return:
    """
    pairings = SecretSantaPair.query.filter_by(year=datetime.datetime.now().year).all()
    result = []
    for pairing in pairings:
        giver = db.query(User).filter_by(id=pairing.giver_id).first()
        receiver = db.query(User).filter_by(id=pairing.receiver_id).first()
        result.append({
            "giver": giver.name,
            "receiver": receiver.name
        })
    return result
