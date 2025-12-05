from fastapi import FastAPI

app = FastAPI(title="My Ghibli World API")

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}
