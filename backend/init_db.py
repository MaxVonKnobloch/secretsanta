# Script to initialize the database and add the admin user
import datetime

from backend.db import User, Base, DATABASE_URL, SecretSantaPair
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.pairing import create_secret_santa_pairs

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)


# Add admin user if not present
def add_admin():
    db = SessionLocal()
    admin = db.query(User).filter_by(name="admin").first()
    if not admin:
        admin = User(name="admin", token="admin")
        db.add(admin)
        db.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
    db.close()


def add_users():
    users = [
        "Max",
        "Anka",
        "Roswitha",
        "Jürgen",
        "Katharina",
        "Christoph"
    ]
    db = SessionLocal()
    for username in users:
        user = db.query(User).filter_by(name=username).first()
        if not user:
            user = User(name=username, token=username)
            db.add(user)
            print(f"User '{username}' created.")
        else:
            print(f"User '{username}' already exists.")
    db.commit()
    db.close()


def add_pairing(pairings: dict, year: str):
    # create 3 pairs out of the 6 users
    db = SessionLocal()

    for giver_name, receiver_name in pairings.items():
        giver = db.query(User).filter_by(name=giver_name).first()
        receiver = db.query(User).filter_by(name=receiver_name).first()

        existing_pair = db.query(SecretSantaPair).filter_by(giver_id=giver.id, year=year).first()
        if not existing_pair:
            pair = SecretSantaPair(giver_id=giver.id, receiver_id=receiver.id, year=year)
            db.add(pair)
            print(f"Pair ({giver.name} -> {receiver.name}) created for year {year}.")
        else:
            print(f"Pair for giver '{giver.name}' and year {year} already exists with receiver {pair.receiver_id}")

    db.commit()
    db.close()


def init_gifts():
    from backend.gifts import Gift
    db = SessionLocal()
    gifts = [
        {
            "title": "Lego Set",
            "description": "A cool Lego set for building fun.",
            "link": "https://www.lego.com/en-us/product/lego-city-police-station-60246",
            "created_by_name": "Max",
            "created_for_name": "Anka"
        },
        {
            "title": "Cookbook",
            "description": "A cookbook with delicious recipes.",
            "link": "https://www.amazon.com/dp/198482218X",
            "created_by_name": "Anka",
            "created_for_name": "Max"
        },
        {
            "title": "Board Game",
            "description": "A fun board game for family nights.",
            "link": "https://www.amazon.com/dp/B00J4E8KX2",
            "created_by_name": "Roswitha",
            "created_for_name": "Jürgen"
        },
        {
            "title": "Wireless Headphones",
            "description": "Noise-cancelling wireless headphones.",
            "link": "https://www.amazon.com/dp/B07Y2ZQ3M3",
            "created_by_name": "Jürgen",
            "created_for_name": "Roswitha"
        },
        {
            "title": "Yoga Mat",
            "description": "A comfortable yoga mat for daily practice.",
            "link": "https://www.amazon.com/dp/B01N6S4A2M",
            "created_by_name": "Katharina",
            "created_for_name": "Christoph"
        },
        {
            "title": "Travel Mug",
            "description": "A stainless steel travel mug.",
            "link": "https://www.amazon.com/dp/B01N5IB20Q",
            "created_by_name": "Christoph",
            "created_for_name": "Katharina"
        }
    ]
    year = datetime.datetime.now().year
    for gift_data in gifts:
        created_by = db.query(User).filter_by(name=gift_data["created_by_name"]).first()
        created_for = db.query(User).filter_by(name=gift_data["created_for_name"]).first()
        if created_by and created_for:
            existing_gift = db.query(Gift).filter_by(
                title=gift_data["title"],
                created_by_id=created_by.id,
                created_for_id=created_for.id,
                year=year
            ).first()
            if not existing_gift:
                gift = Gift(
                    title=gift_data["title"],
                    description=gift_data["description"],
                    link=gift_data["link"],
                    created_by_id=created_by.id,
                    created_for_id=created_for.id,
                    year=year
                )
                db.add(gift)
                print(
                    f"Gift '{gift_data['title']}' from '{gift_data['created_by_name']}' to '{gift_data['created_for_name']}' created.")
            else:
                print(
                    f"Gift '{gift_data['title']}' from '{gift_data['created_by_name']}' to '{gift_data['created_for_name']}' already exists.")
    db.commit()
    db.close()


if __name__ == "__main__":
    add_admin()
    add_users()
    add_pairing(year="2024", pairings={
            "Max": "Katharina",
            "Katharina": "Jürgen",
            "Roswitha": "Max",
            "Jürgen": "Christoph",
            "Anka": "Roswitha",
            "Christoph": "Anka"
        })
    add_pairing(year="2025", pairings={
        "Max": "Jürgen",
        "Katharina": "Roswitha",
        "Roswitha": "Christoph",
        "Jürgen": "Anka",
        "Anka": "Katharina",
        "Christoph": "Max"
    })
    #init_gifts()
