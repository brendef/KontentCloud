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


# redirect url for isntagram authorization
@router.get("/auth")
async def auth(code: str):

    redirectUri = "https://localhost:8000/auth/"  # the same as this end point
    instagram = Instagram(redirectUri=redirectUri, code=code)

    shortToken = instagram.get_token()
    longTokenResponse = instagram.exchange_token(shortToken)

    longToken = longTokenResponse["longToken"]  # long lived token
    ttl = longTokenResponse["ttl"]  # time to live / expires in seconds

    # Set cookie for long lived token
    response = RedirectResponse(url="/feed")
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


@router.get("/logout")
def logout():

    response = RedirectResponse(url="/login")

    response.delete_cookie(key="longToken")
    response.delete_cookie(key="tokenTtl")

    return response


@router.get("/feed")
def home(request: Request):

    # get the cookie from the request
    cookieLongToken = request.cookies.get("longToken")

    instagram = Instagram(token=cookieLongToken)
    feed = instagram.get_feed()

    return templates.TemplateResponse(
        request=request, name="pages/feed.html", context={"feed": feed}
    )
