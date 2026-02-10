from fastmcp import FastMCP

mcp = FastMCP("todo-app")

# Todos List

todos = [
    {
        "id": "1",
        "Activity": "Jogging for 2 hours at 7:00 AM."
    },
    {
        "id": "2",
        "Activity": "Writing 3 pages of my new book at 2:00 PM."
    }
]

# A minimal app to demonstrate the get request

@mcp.tool
def root() -> dict:
    return {"Ping": "Pong"}

@mcp.tool
def get_todos() -> dict:
    return {"Data": todos}

@mcp.tool
def add_todo(todo: dict) -> dict: 
    todos.append(todo)
    return {
        "data": "A Todo is Added!"
    }

@mcp.tool
def update_todo(id: int, body: dict) -> dict:
    for todo in todos:
        if (int(todo["id"])) == id:
            todo["Activity"] = body["Activity"]
            return {
                "data": f"Todo with id {id} has been updated"
            }
    return {
        "data": f"This Todo with id {id} is not found!"
    }

@mcp.tool
def delete_todo(id: int) -> dict:
    for todo in todos:
        if int(todo["id"]) == id:
            todos.remove(todo)
            return{
                "data": f"Todo with id {id} has been deleted!"
            }
    return {
        "data": f"Todo with id {id} was not found!"
    }


if __name__ == "__main__":
    mcp.run()