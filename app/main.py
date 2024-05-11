from routes import router
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


def main():

    app = FastAPI()  # create fast api instance as app
    app.include_router(router)  # routes from the routes.py file

    # mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # load environment variables
    load_dotenv()

    return app


app = main()
