import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, auth, database
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        return db.query(models.User).filter(models.User.username == username).first()
    except:
        raise HTTPException(status_code=401)

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return {"status": "success"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong credentials")
    return {"access_token": auth.create_access_token({"sub": user.username}), "token_type": "bearer"}

@app.get("/tasks")
def tasks(user=Depends(get_user)):
    return user.tasks

@app.post("/tasks")
def add_task(task: schemas.TaskBase, db: Session = Depends(get_db), user=Depends(get_user)):
    new_task = models.Task(title=task.title, owner_id=user.id)
    db.add(new_task)
    db.commit()
    return {"status": "added"}

@app.put("/tasks/{id}")
def toggle_task(id: int, db: Session = Depends(get_db), user=Depends(get_user)):
    task = db.query(models.Task).filter(models.Task.id == id, models.Task.owner_id == user.id).first()
    task.completed = not task.completed
    db.commit()
    return {"status": "updated"}

@app.delete("/tasks/{id}")
def del_task(id: int, db: Session = Depends(get_db), user=Depends(get_user)):
    task = db.query(models.Task).filter(models.Task.id == id, models.Task.owner_id == user.id).first()
    db.delete(task)
    db.commit()
    return {"status": "deleted"}

# Serve Frontend
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def home():
    return FileResponse("static/index.html")