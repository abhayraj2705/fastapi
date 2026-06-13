from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

todos = []

class Todo(BaseModel):
    id: int
    title: str
    completed: bool


@app.post("/todos")
def create_todo(todo: Todo):
    todos.append(todo)

    return {
        "message": "The todo is created successfully",
        "data": todo
    }


@app.get("/todos")
def get_todos():
    return {
        "message": "All todos fetched successfully",
        "data": todos
    }


@app.get("/todos/{todo_id}")
def get_single_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return {
                "message": "Todo found successfully",
                "data": todo
            }

    return {
        "error": "Todo not found"
    }


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos[index] = updated_todo

            return {
                "message": "Todo updated successfully",
                "data": updated_todo
            }

    return {
        "error": "Todo not found"
    }


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            deleted_todo = todos.pop(index)

            return {
                "message": "Todo deleted successfully",
                "data": deleted_todo
            }

    return {
        "error": "Todo not found"
    }