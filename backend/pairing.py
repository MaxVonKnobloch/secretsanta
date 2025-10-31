import datetime
import random
from backend.db import SecretSantaPair
from backend.db import User

forbidden_combinations = {
    "Max": ["Anka"],
    "Anka": ["Max"],
    "Katharina": ["Christoph"],
    "Christoph": ["Katharina"],
    "Roswitha": ["Jürgen"],
    "Jürgen": ["Roswitha"],
}


def get_last_year_pairs(db, year: int):
    return db.query(SecretSantaPair).filter(SecretSantaPair.year == year).all()


def create_secret_santa_pairs(db, allow_last_year_pairing: bool = False, allow_vice_versa: bool = False):
    """
    This function gets all users that are not admin and creates secret santa pairs for them,
    ensuring that no user is paired with themselves or with users in their forbidden list or with the same user as last year.
    :return: Nothing, stores the pairs in the database.
    """

    users = db.query(User).filter(User.name != "admin").all()
    user_names = [user.name for user in users]
    name_to_user = {user.name: user for user in users}

    current_year = datetime.datetime.now().year
    last_year_pairs = get_last_year_pairs(db, current_year - 1)
    last_year_dict = {pair.giver.name: pair.receiver.name for pair in last_year_pairs}

    max_attempts = 1000
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        shuffled_names = user_names[:]
        random.shuffle(shuffled_names)

        valid = True
        pairs = {}
        for giver_name, receiver_name in zip(user_names, shuffled_names):
            if giver_name == receiver_name:
                valid = False
            if receiver_name in forbidden_combinations.get(giver_name, []):
                valid = False

            if not allow_last_year_pairing and last_year_dict.get(giver_name) == receiver_name:
                valid = False

            if not allow_vice_versa and pairs.get(receiver_name) == giver_name:
                valid = False

            if not valid:
                break
            pairs[giver_name] = receiver_name

        if valid:
            for giver_name, receiver_name in pairs.items():
                giver = name_to_user[giver_name]
                receiver = name_to_user[receiver_name]
                pair = SecretSantaPair(giver_id=giver.id, receiver_id=receiver.id, year=current_year)
                db.add(pair)
            db.commit()
            print(f"Secret Santa pairs created successfully on try {attempts}")
            return

    print("Failed to create valid Secret Santa pairs after multiple attempts.")
