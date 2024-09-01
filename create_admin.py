# create_admin.py

from models import User, Base, engine, SessionLocal
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if not admin_user:
            hashed_password = pwd_context.hash(ADMIN_PASSWORD)
            admin_user = User(
                username=ADMIN_USERNAME,
                hashed_password=hashed_password,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("Администратор создан.")
        else:
            print("Администратор уже существует.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
