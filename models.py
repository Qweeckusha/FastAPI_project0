from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Подключение к MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://admin:12365487sql@localhost:3307/users"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Зависимость для работы с базой данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=False, index=True)
    hashed_password = Column(String(255))

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)
