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

@app.middleware("http")
async def add_cache_control_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

@app.get('/about', response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse('about.html', {"request": request})

@app.get('/promo', response_class=HTMLResponse)
async def promo_page(request: Request):
    return templates.TemplateResponse('promo.html', {"request": request})

@app.post("/add_user", response_class=HTMLResponse)
async def add_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    with db:
        db.add(User(username=username, hashed_password=hashed_password))
        db.commit()
        users = db.query(User).all()
    return templates.TemplateResponse('index.html', {"request": request, "users": users})
