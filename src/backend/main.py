from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Optional, Annotated
import google.generativeai as genai
import os
from dotenv import load_dotenv

from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import date
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="To-Do List API with Persistent Database")

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Error configuring Google Gemini API: {e}")
    gemini_model = None

DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Creates the database tables if they don't exist."""
    print("--- Attempting to create database tables ---")
    try:
        SQLModel.metadata.create_all(engine)
        print("--- Database tables created (if they didn't exist) ---")
    except Exception as e:
        print(f"--- ERROR creating database tables: {e} ---")

def get_session():
    with Session(engine) as session:
        yield session

class TodoItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[str] = Field(default=None, max_length=50)
    due_date: Optional[date] = Field(default=None)

class TodoItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TranslationResponse(BaseModel):
    translated_text: str

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the To-Do List API (with Persistent Database)!"}

@app.get("/todos", response_model=List[TodoItem])
async def get_all_todos(session: Annotated[Session, Depends(get_session)]):
    print("--- Fetching all todos from DB ---")
    todos = session.exec(select(TodoItem)).all()
    print(f"--- Found {len(todos)} todos ---")
    return todos

@app.post("/todos", response_model=TodoItem, status_code=201)
async def create_todo(todo_create: TodoItemCreate, session: Annotated[Session, Depends(get_session)]):
    print(f"--- Received TodoItemCreate: {todo_create} ---")
    db_todo = TodoItem.model_validate(todo_create)
    print(f"--- Converted to TodoItem for DB: {db_todo} ---")
    try:
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        print(f"--- Successfully added todo to DB. ID: {db_todo.id} ---")
        return db_todo
    except Exception as e:
        print(f"--- ERROR during todo creation and DB commit: {e} ---")
        raise HTTPException(status_code=500, detail=f"Failed to create todo: {e}")


@app.get("/todos/{todo_id}", response_model=TodoItem)
async def get_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    print(f"--- Fetching todo with ID: {todo_id} ---")
    todo = session.get(TodoItem, todo_id)
    if not todo:
        print(f"--- Todo with ID {todo_id} not found ---")
        raise HTTPException(status_code=404, detail="To-Do item not found")
    print(f"--- Found todo: {todo.title} ---")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: int, todo_update: TodoItemUpdate, session: Annotated[Session, Depends(get_session)]):
    print(f"--- Attempting to update todo ID: {todo_id} with data: {todo_update} ---")
    todo = session.get(TodoItem, todo_id)
    if not todo:
        print(f"--- Todo with ID {todo_id} not found for update ---")
        raise HTTPException(status_code=404, detail="To-Do item not found")

    update_data = todo_update.model_dump(exclude_unset=True)
    print(f"--- Update data (excluding unset): {update_data} ---")
    todo.sqlmodel_update(update_data)

    try:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        print(f"--- Successfully updated todo ID: {todo.id} ---")
        return todo
    except Exception as e:
        print(f"--- ERROR during todo update and DB commit: {e} ---")
        raise HTTPException(status_code=500, detail=f"Failed to update todo: {e}")

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    print(f"--- Attempting to delete todo ID: {todo_id} ---")
    todo = session.get(TodoItem, todo_id)
    if not todo:
        print(f"--- Todo with ID {todo_id} not found for deletion ---")
        raise HTTPException(status_code=404, detail="To-Do item not found")

    try:
        session.delete(todo)
        session.commit()
        print(f"--- Successfully deleted todo ID: {todo_id} ---")
        return
    except Exception as e:
        print(f"--- ERROR during todo deletion and DB commit: {e} ---")
        raise HTTPException(status_code=500, detail=f"Failed to delete todo: {e}")

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    if not gemini_model:
        raise HTTPException(status_code=503, detail="Translation service not available. API key might be missing or invalid.")
    try:
        prompt = f"Translate the following text into {request.target_language}: {request.text}"
        response = gemini_model.generate_content(prompt)
        translated_content = response.text
        return TranslationResponse(translated_text=translated_content)
    except Exception as e:
        print(f"Gemini translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to translate text: {e}")