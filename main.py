import bcrypt
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models import User, Base, engine, get_db

app = FastAPI()

app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

Base.metadata.create_all(bind=engine)

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse('index.html', {"request": request, "users": users})


@app.post("/add_user", response_class=HTMLResponse)
async def add_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, hashed_password=hashed_password.decode('utf-8'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    users = db.query(User).all()
    return templates.TemplateResponse('index.html', {"request": request, "users": users})