from fastapi import FastAPI, Depends, HTTPException, status, Path  # Depends injects dependencies; HTTPException returns error responses; Path validates path params
from typing import Annotated  # Annotated bundles a type hint with extra metadata (used for dependency injection)
from sqlalchemy.orm import Session  # Session represents an active database connection/transaction
import models  # import models module so SQLAlchemy is aware of all table definitions
from models import Todo  # import Todo class directly for use in queries
from database import engine, SessionLocal  # engine is the DB connection; SessionLocal creates new DB sessions
from pydantic import BaseModel, Field  # BaseModel defines request schemas; Field adds validation rules

models.Base.metadata.create_all(bind=engine)  # creates all tables defined in models.py in the database if they don't already exist

app = FastAPI()  # create the FastAPI application instance


def get_db():  # dependency function that provides a database session to route handlers
    db = SessionLocal()  # open a new database session
    try:
        yield db  # hand the session to the caller; execution pauses here until the request is done
    finally:
        db.close()  # always close the session after the request, even if an error occurred


db_dependency = Annotated[Session, Depends(get_db)]  # reusable type alias that tells FastAPI to inject a DB session via get_db into any route that declares this type


class TodoRequest(BaseModel):  # Pydantic model used to validate incoming request body data
    title: str = Field(min_length=3)  # title must be at least 3 characters
    description: str = Field(min_length=3, max_length=100)  # description between 3 and 100 characters
    priority: int = Field(gt=0, lt=8)  # priority must be between 1 and 7
    completed: bool  # completed status — True or False


@app.get("/")  # GET / — returns all todos from the database
async def root(db: db_dependency):  # FastAPI automatically injects the DB session via db_dependency
    return db.query(Todo).all()  # query the todos table and return all records as a list


@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)  # GET /todos/{id} — returns a single todo by its ID with 200 OK
async def get_todo(db: db_dependency, todo_id: int = Path(gt=0)):  # Path(gt=0) ensures todo_id must be greater than 0
    todo = db.query(Todo).filter(Todo.id == todo_id).first()  # query for the first todo matching the given ID
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")  # raise 404 if no matching todo found
    return todo


@app.post("/todos", status_code=status.HTTP_201_CREATED)  # POST /todos — creates a new todo, returns 201 Created
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todo(**todo_request.model_dump())  # model_dump() converts the Pydantic model to a dict; ** unpacks it into the Todo constructor
    db.add(todo_model)  # stage the new todo to be inserted into the database
    db.commit()  # persist the change to the database


@app.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)  # PUT /todos/{id} — updates an existing todo, returns 204 No Content
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()  # fetch the existing todo by ID
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")  # raise 404 if no matching todo found
    todo.title = todo_request.title  # update title field on the fetched object
    todo.description = todo_request.description  # update description field
    todo.priority = todo_request.priority  # update priority field
    todo.completed = todo_request.completed  # update completed field
    db.add(todo)  # stage the updated todo — SQLAlchemy tracks the changes
    db.commit()  # persist the changes to the database


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE /todos/{id} — deletes a todo by ID, returns 204 No Content
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()  # fetch the todo to be deleted
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")  # raise 404 if no matching todo found
    db.delete(todo)  # stage the todo for deletion
    db.commit()  # persist the deletion to the database
