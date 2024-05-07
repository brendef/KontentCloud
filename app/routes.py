from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from models.facebook import Instagram

router = APIRouter()  # init app router
templates = Jinja2Templates(directory="templates")  # load html templates


# index route
@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request=request, name="pages/index.html")


# where user clicks to login
@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse(request=request, name="pages/login.html")


# search for a user but for now is where user is redirected after login
@router.get("/search")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="pages/search.html")


# redirect url for isntagram authorization
@router.get("/auth")
async def auth(code: str):

    redirectUri = "https://localhost:8000/auth/"  # the same as this end point
    instagram = Instagram(redirectUri, code)

    shortToken = instagram.get_token()
    longTokenResponse = instagram.exchange_token(shortToken)

    longToken = longTokenResponse["longToken"]  # long lived token
    ttl = longTokenResponse["ttl"]  # time to live / expires in seconds

    # Set cookie for long lived token
    response = RedirectResponse(url="/search")
    response.set_cookie(
        key="longToken",
        value=longToken,
        expires=datetime.now(timezone.utc) + timedelta(seconds=ttl),
        secure=True,
        httponly=True,
    )

    # Set cookie for ttl
    response.set_cookie(
        key="tokenTtl",
        value=ttl,
        expires=datetime.now(timezone.utc) + timedelta(seconds=ttl),
        secure=True,
        httponly=False,
    )

    return response
