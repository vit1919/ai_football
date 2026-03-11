import uvicorn
from fastapi import FastAPI
from pathlib import Path

app = FastAPI()

@app.get('/hello-world')
def hello_world():
    return {'message': "Hello"}




if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=str(project_root),
    )