from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    print('API Funcionando')
    return { "message": "API Funcionando" }





































