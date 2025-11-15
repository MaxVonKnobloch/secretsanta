import datetime
import logging

from backend import config
from backend.db import User, SecretSantaPair, Gift, Vote
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Union, List

from backend.link_preview import preview_external_links


class GiftOut(BaseModel):
    pk: int
    title: str
    created_by_name: str
    created_for_name: str
    votes: Union[str, int]
    preview_image_path: str
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
            votes = 0
        gift_list.append(GiftOut(
            pk=gift.id,
            title=gift.title,
            created_by_name=gift.created_by.name,
            created_for_name=gift.created_for.name,
            votes=votes,
            link=gift.link if hasattr(gift, 'link') else None,
            preview_image_path=gift.preview_image_path if gift.preview_image_path else config.default_preview_image_path
        ))

    return UserGiftList(
        pk=user.id,
        username=user.name,
        gifts=gift_list
    )


def add_or_update_gift(db: Session,
                       title: str,
                       created_by: User,
                       created_for: User,
                       year: int = None,
                       description: str = "",
                       link: str = "",
                       gift_pk: int = None) -> GiftOut:
    """
    Adds a new gift or updates an existing gift.
    If gift_pk is provided, updates the existing gift with that primary key.
    """
    if year is None:
        year = datetime.datetime.now().year

    is_new_gift = gift_pk is None
    if is_new_gift:
        gift = Gift(
            title=title,
            description=description,
            link=link,
            year=year,
            created_by=created_by,
            created_by_id=created_by.id,
            created_for=created_for,
            created_for_id=created_for.id
        )
    else:
        gift = db.query(Gift).filter_by(id=gift_pk).first()
        if gift is None:
            raise ValueError("Gift with the given primary key does not exist.")

        gift.title = title
        gift.description = description
        gift.link = link
        gift.year = year
        gift.created_by = created_by
        gift.created_by_id = created_by.id
        gift.created_for = created_for
        gift.created_for_id = created_for.id

    if gift.link:
        logging.info(f"Generating preview for link: {gift.link}")
        gift.preview_image_path = preview_external_links(gift.link)
    else:
        logging.info("No link provided, using default preview image.")
        gift.preview_image_path = config.default_preview_image_path

    if is_new_gift:
        db.add(gift)

    db.commit()

    return GiftOut(
        pk=gift.id,
        title=gift.title,
        created_by_name=created_by.name,
        created_for_name=created_for.name,
        votes=0,
        preview_image_path=gift.preview_image_path,
        link=gift.link
    )