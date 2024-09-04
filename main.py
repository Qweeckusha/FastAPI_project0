import bcrypt
from fastapi import Cookie, FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from models import User, Base, engine, get_db

app = FastAPI()

app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

Base.metadata.create_all(bind=engine)

# Настройки для токенов
SECRET_KEY = "GjhbdfgjHbJK76JjhgLSds68jJd9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")






# Funcs --------------------------------------------------------------

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    if access_token is None:
        return None

    try:
        payload = jwt.decode(access_token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

    except JWTError as e:
        raise e

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return None
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user






# Middleware --------------------------------------------------------------

@app.middleware("http")
async def add_cache_control_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response






# Routers --------------------------------------------------------------

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request, current_user: User = Depends(get_current_user)):
    try:
        return templates.TemplateResponse('index.html', {"request": request, "user": current_user})
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return templates.TemplateResponse('index.html', {"request": request, "user": None})
        raise e
            

@app.get('/about', response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse('about.html', {"request": request})

@app.get('/promo', response_class=HTMLResponse)
async def promo_page(request: Request):
    return templates.TemplateResponse('promo.html', {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("reg.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token")  # Удаляем access_token из куки
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_admin_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})






# Handlers --------------------------------------------------------------

@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Проверка на наличие пользователя с таким же логином
    user = db.query(User).filter(User.username == username).first()
    if user:
        return templates.TemplateResponse("reg.html", {"request": request, "error": 'Пользователь с таким именем уже есть.', "success": None})
            
    
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return templates.TemplateResponse("login.html", {"request": request, "success": "Регистрация прошла успешно. Теперь вы можете войти."})

@app.post("/login")
async def login_for_access_token(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": 'Логин или пароль указаны неверно.'})
        
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

