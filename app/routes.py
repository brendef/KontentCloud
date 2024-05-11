from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from models.facebook import Instagram

router = APIRouter()  # init app router
templates = Jinja2Templates(directory="templates")  # load html templates

# Constants
LONG_TOKEN = "longToken"
TOKEN_TTL = "tokenTtl"
TTL = "ttl"

# Redirect Constants
LoginRedirect = "/feed"
LoggedOutRedirect = "/login"


# redirect url for isntagram authorization
@router.get("/auth")
async def auth(code: str):

    redirectUri = "https://localhost:8000/auth/"  # the same as this end point
    instagram = Instagram(redirectUri=redirectUri, code=code)

    shortToken = instagram.get_token()
    longTokenResponse = instagram.exchange_token(shortToken)

    longToken = longTokenResponse[LONG_TOKEN]  # long lived token
    ttl = longTokenResponse[TTL]  # time to live / expires in seconds

    # Set cookie for long lived token
    response = RedirectResponse(url=LoginRedirect)
    response.set_cookie(
        key=LONG_TOKEN,
        value=longToken,
        expires=datetime.now(timezone.utc) + timedelta(seconds=ttl),
        secure=True,
        httponly=True,
    )

    # Set cookie for ttl
    response.set_cookie(
        key=TOKEN_TTL,
        value=ttl,
        expires=datetime.now(timezone.utc) + timedelta(seconds=ttl),
        secure=True,
        httponly=False,
    )

    return response


@router.get("/logout")
def logout():

    response = RedirectResponse(url=LoggedOutRedirect)

    response.delete_cookie(key=LONG_TOKEN)
    response.delete_cookie(key=TOKEN_TTL)

    return response


# template routes


# index route
@router.get("/")
def index_template(request: Request):
    return templates.TemplateResponse(request=request, name="pages/index.html")


# where user clicks to login
@router.get("/login")
def login_template(request: Request):
    return templates.TemplateResponse(request=request, name="pages/login.html")


# display the users instagram feed, once authenticated
@router.get("/feed")
def feed_template(request: Request):

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)

    instagram = Instagram(token=cookieLongToken)
    user = instagram.get_user()
    feed = instagram.get_feed()

    return templates.TemplateResponse(
        request=request, name="pages/feed.html", context={"user": user, "feed": feed}
    )


@router.get("/get-feed/")
def feed_htmx(request: Request, nextUrl: str):

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)

    instagram = Instagram(token=cookieLongToken)
    feed = instagram.get_next_feed(nextUrl)

    htmlResponse = ""

    for num, image in enumerate(feed["data"]):
        if image["media_type"] == "VIDEO":
            continue

        htmlResponse += f"""<div id="{num+1003302*123}" hx-on:click="selectImage('{{ image.media_url }}', this.id)"> <img src="{image["media_url"]}" alt="" /> </div>"""

    if "next" in feed["paging"]:
        htmlResponse += f"""<div hx-get="/get-feed" hx-vars="{{ 'nextUrl':'{feed["paging"]["next"]}' }}" hx-trigger="revealed" hx-swap="outerHTML">
            <div class="text-center">
                <div role="status">
                    <svg aria-hidden="true" class="inline w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
                        <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
                    </svg>
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
        </div>
        """

    return HTMLResponse(content=htmlResponse)
