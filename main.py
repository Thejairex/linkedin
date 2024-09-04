from fastapi import FastAPI, Form
from threading import Thread

from linkedin import Searcher

import os
app = FastAPI()


searcher = Searcher()

@app.get("/")
def read_root():
    return {"Hello": "World",
            "current_page": searcher.driver.current_url}

# Función para ejecutar la búsqueda en un hilo separado
def background_search(keyword, page_number):
    searcher.search_jobs(page_number)

@app.get("/search")
def search(keyword: str, page_number: int):
    if not searcher.loggedin:
        return {"message": "Por favor inicia sesión."}
    # Ejecutamos la búsqueda en segundo plano
    searcher_thread = Thread(target=background_search, args=(keyword, page_number))
    searcher_thread.start()
    
    return {"message": "La búsqueda se está ejecutando en segundo plano."}

@app.get("/jobs")
def get_jobs():
    return searcher.get_jobs()

@app.get("/logintest")
def logintest():
    searcher.login(os.getenv('EMAIL'), os.getenv('PASSWORD'))
    return {"message": "Se ha iniciado sesión."}

@app.get("/login")
def login(user_email: str = Form(...), user_password: str = Form(...)):
    searcher.login(user_email, user_password)
    return {"message": "Se ha iniciado sesión."}
    