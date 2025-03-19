from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import time 
from pathlib import Path

app = FastAPI()

origins = [
    "*",  
    # "http://localhost:5173",
]

# Add CORSMiddleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


class ToDo(BaseModel):
    title: str
    date: str  # Date format should be 'YYYY-MM-DD'
    priority: dict  
    description: str
    status: str = Field(default="Incomplete") 
    id: int = None  

TODO_FILE_PATH = Path("todos.json")

# Helper function to read todos from the JSON file
def read_todos():
    if TODO_FILE_PATH.exists():
        with open(TODO_FILE_PATH, "r") as f:
            return json.load(f)
    return []

# Helper function to write todos to the JSON file
def write_todos(todos):
    with open(TODO_FILE_PATH, "w") as f:
        json.dump(todos, f, indent=4)

# POST route to create a new todo
@app.post("/todos")
def create_todo(todo: ToDo):
    # Validate priority to ensure one of them is True
    if not any(todo.priority.values()):
        raise HTTPException(status_code=400, detail="At least one priority must be True.")

    todos = read_todos()

    new_id = int(time.time() * 1000) 

    new_todo = {
        "id": new_id,
        "title": todo.title,
        "date": todo.date,
        "priority": todo.priority,
        "description": todo.description,
        "status": todo.status  
    }

    todos.append(new_todo)

    write_todos(todos)

    return new_todo

# Route to get all todos
@app.get("/alltodos")
def get_all_todos():
    todos = read_todos()
    return todos


# DELETE route to delete a todo by id
@app.delete("/todos/{id}")
def delete_todo(id: int):

    todos = read_todos()

    todo_to_delete = next((todo for todo in todos if todo["id"] == id), None)

    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todos = [todo for todo in todos if todo["id"] != id]

    write_todos(todos)

    return {"message": "Todo deleted successfully", "id": id}

# PATCH route to update status of a todo to "Complete"
@app.patch("/todo_complete/{id}")
def update_todo_status(id: int):

    todos = read_todos()

    todo_to_update = next((todo for todo in todos if todo["id"] == id), None)

    if todo_to_update is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_to_update["status"] = "Complete"

    write_todos(todos)

    return {"message": "Todo status updated successfully", "id": id, "status": "Complete"}


# PATCH route to update a todo by id
@app.patch("/todos/{id}")
def update_todo(id: int, todo: ToDo):

    todos = read_todos()

    todo_to_update = next((todo for todo in todos if todo["id"] == id), None)

    if todo_to_update is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.title:
        todo_to_update["title"] = todo.title
    if todo.date:
        todo_to_update["date"] = todo.date
    if todo.priority:
        todo_to_update["priority"] = todo.priority
    if todo.description:
        todo_to_update["description"] = todo.description
    if todo.status:
        todo_to_update["status"] = todo.status

    write_todos(todos)

    return {"message": "Todo updated successfully", "todo": todo_to_update}