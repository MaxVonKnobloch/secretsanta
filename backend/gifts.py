import datetime
from backend.db import User, SecretSantaPair, Gift, Vote
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Union, List


class GiftOut(BaseModel):
    pk: int
    title: str
    created_by_name: str
    votes: Union[str, int]
    link: str | None = None


class UserGiftList(BaseModel):
    pk: int
    username: str
    gifts: List[GiftOut]


def get_receiver(user: User, db: Session, year: int = None) -> User | None:
    """
    Returns the receiver User object for the given user and year.
    """
    if year is None:
        year = datetime.datetime.now().year
    pair = db.query(SecretSantaPair).filter_by(giver_id=user.id, year=year).first()
    return pair.receiver if pair and pair.receiver else None


def get_own_gift_list(user: User, db: Session, year: int = None) -> UserGiftList:
    own_gift_list = get_gift_list(user, db, year)
    own_gift_list.gifts = [g for g in own_gift_list.gifts if g.created_by_name == user.name]
    return own_gift_list


def get_gift_list(user: User, db: Session, year: int = None, current_user: User = None) -> UserGiftList:
    """
    Returns a list of GiftOut for each gift for a user in a given year.
    If current_user is provided, includes the vote by current_user for each gift.
    """
    if year is None:
        year = datetime.datetime.now().year
    gifts = db.query(Gift).filter_by(created_for_id=user.id, year=year).all()
    gift_list = []
    for gift in gifts:
        if current_user:
            vote = db.query(Vote).filter_by(gift_id=gift.id, user_id=current_user.id).first()
            votes = vote.value if vote else "undefined"
        else:
            votes = "undefined"
        gift_list.append(GiftOut(
            pk=gift.id,
            title=gift.title,
            created_by_name=gift.created_by.name if gift.created_by else "",
            votes=votes,
            link=gift.links if hasattr(gift, 'links') else None
        ))

    return UserGiftList(
        pk=user.id,
        username=user.name,
        gifts=gift_list
    )
