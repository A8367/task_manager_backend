from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import time  # For generating unique ids based on current time
from pathlib import Path

# Initialize FastAPI
app = FastAPI()

# Allow CORS for all domains (you can restrict this to specific origins if needed)
origins = [
    "*",  
]

# Add CORSMiddleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins (for security, specify allowed domains here)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define the root route
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Define the ToDo model with an id field
class ToDo(BaseModel):
    title: str
    date: str  # Date format should be 'YYYY-MM-DD'
    priority: dict  # Should contain 'extreme', 'moderate', and 'low' as keys
    description: str
    status: str = Field(default="Incomplete")  # Set default value for status
    id: int = None  # ID will be auto-assigned, so it's not passed from frontend

# Path to the local JSON file where todos will be stored
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

    # Read current todos from file
    todos = read_todos()

    # Generate a new id based on the current time (milliseconds since epoch)
    new_id = int(time.time() * 1000)  # Multiply by 1000 to get milliseconds

    # Create a new todo dictionary, including the generated id
    new_todo = {
        "id": new_id,
        "title": todo.title,
        "date": todo.date,
        "priority": todo.priority,
        "description": todo.description,
        "status": todo.status  # status will default to "Incomplete"
    }

    # Add the new todo to the list
    todos.append(new_todo)

    # Write updated todos back to the file
    write_todos(todos)

    # Return the created todo as a response
    return new_todo

# Route to get all todos
@app.get("/alltodos")
def get_all_todos():
    todos = read_todos()
    return todos


# DELETE route to delete a todo by id
@app.delete("/todos/{id}")
def delete_todo(id: int):
    # Read current todos from file
    todos = read_todos()

    # Find the todo with the matching id
    todo_to_delete = next((todo for todo in todos if todo["id"] == id), None)

    if todo_to_delete is None:
        # If no todo with the given id is found, raise a 404 error
        raise HTTPException(status_code=404, detail="Todo not found")

    # Remove the todo from the list
    todos = [todo for todo in todos if todo["id"] != id]

    # Write the updated todos back to the file
    write_todos(todos)

    return {"message": "Todo deleted successfully", "id": id}

# PATCH route to update status of a todo to "Complete"
@app.patch("/todo_complete/{id}")
def update_todo_status(id: int):
    # Read current todos from file
    todos = read_todos()

    # Find the todo with the matching id
    todo_to_update = next((todo for todo in todos if todo["id"] == id), None)

    if todo_to_update is None:
        # If no todo with the given id is found, raise a 404 error
        raise HTTPException(status_code=404, detail="Todo not found")

    # Update the status to "Complete"
    todo_to_update["status"] = "Complete"

    # Write the updated todos back to the file
    write_todos(todos)

    return {"message": "Todo status updated successfully", "id": id, "status": "Complete"}


# PATCH route to update a todo by id (title, description, date, priority, status)
@app.patch("/todos/{id}")
def update_todo(id: int, todo: ToDo):
    # Read current todos from file
    todos = read_todos()

    # Find the todo with the matching id
    todo_to_update = next((todo for todo in todos if todo["id"] == id), None)

    if todo_to_update is None:
        # If no todo with the given id is found, raise a 404 error
        raise HTTPException(status_code=404, detail="Todo not found")

    # Update the fields with the provided data (partial update)
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

    # Write the updated todos back to the file
    write_todos(todos)

    return {"message": "Todo updated successfully", "todo": todo_to_update}