import uuid, json, requests, os

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, WebSocket, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from models.facebook import Instagram
from lib.io import createFolder, zipFolder, deleteFolder

from database.auth import Auth

router = APIRouter()  # init app router
templates = Jinja2Templates(directory="templates")  # load html templates

# Constants
LONG_TOKEN = "longToken"
TOKEN_TTL = "tokenTtl"
TTL = "ttl"
JWT = "jwt"
JWT_TTL = "jwt_ttl"

# Redirect Constants
LoginRedirect = "/home"
LoggedOutRedirect = "/login"
InstagramFeed = "/instagram-feed"


# redirect url for isntagram authorization
@router.get("/authorise-instagram")
async def instagram_auth(code: str):

    redirectUri = (
        "https://localhost:8000/authorise-instagram/"  # the same as this end point
    )
    instagram = Instagram(redirectUri=redirectUri, code=code)

    shortToken = instagram.get_token()
    longTokenResponse = instagram.exchange_token(shortToken)

    longToken = longTokenResponse[LONG_TOKEN]  # long lived token
    ttl = longTokenResponse[TTL]  # time to live / expires in seconds

    # Set cookie for long lived token
    response = RedirectResponse(url=InstagramFeed)
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


# template routes


# index route
@router.get("/")
def index_template(request: Request):
    return templates.TemplateResponse(request=request, name="pages/index.html")


# where user clicks to signup
@router.get("/signup")
def signup_template(request: Request):
    return templates.TemplateResponse(request=request, name="pages/signup.html")


# where user clicks to login
@router.get("/login")
def login_template(request: Request):
    return templates.TemplateResponse(request=request, name="pages/login.html")


# where user clicks to login
@router.get("/home")
def home_template(request: Request):
    return templates.TemplateResponse(request=request, name="pages/home.html")


# display the users instagram feed, once authenticated
@router.get("/instagram-feed")
def feed_template(request: Request):

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)

    instagram = Instagram(token=cookieLongToken)
    user = instagram.get_user()
    feed = instagram.get_feed()

    return templates.TemplateResponse(
        request=request,
        name="pages/instagram-feed.html",
        context={"user": user, "feed": feed},
    )


@router.get("/get-instagram-feed")
def feed_htmx(request: Request, nextUrl: str):

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)

    instagram = Instagram(token=cookieLongToken)
    feed = instagram.get_next_feed(nextUrl)

    htmlResponse = ""

    for image in feed["data"]:
        if image["media_type"] == "VIDEO":
            continue

        imageuuid = str(uuid.uuid4())
        htmlResponse += f"""
        
            <div id="a{imageuuid}" class="image"> <img src="{image["media_url"]}" alt="" /> </div>
            <script>
                document.getElementById("a{imageuuid}").addEventListener('click', (e) => {{
                        selectImage(e.srcElement.src, e.target)
                    }}
                )
            </script>
        """

    if "next" in feed["paging"]:
        htmlResponse += f"""<div hx-get="/get-instagram-feed" hx-vars="{{ 'nextUrl':'{feed["paging"]["next"]}' }}" hx-trigger="revealed" hx-swap="outerHTML">
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


# Websocket route


@router.get("/download-zip")
def download_zip(request: Request, background_tasks: BackgroundTasks):

    userLongToken = request.cookies.get(LONG_TOKEN)
    zipFileLocation = f"tmp/{userLongToken}.zip"

    background_tasks.add_task(os.remove, zipFileLocation)

    return FileResponse(path=zipFileLocation, filename="instagram_images.zip")


@router.websocket("/download-images/ws")
async def download_images(websocket: WebSocket):
    print("Websocket connection opened")
    await websocket.accept()

    userLongToken = websocket.cookies.get(LONG_TOKEN)

    while True:
        jsonMessage = await websocket.receive_text()
        data = json.loads(jsonMessage)

        # if there are no links, close the connecton
        if data.get("links") is None:
            await websocket.close()
            break

        # if the close flag is set, close the connection
        if data.get("close") is not None and data["close"] == True:
            await websocket.close()
            break

        links = data["links"]
        linksAmount = len(links)

        tempImageFolder = f"tmp/{userLongToken}"
        createFolder(tempImageFolder)

        # notify the client that the download is starting and how many images are being downloaded
        await websocket.send_text(f"Downloading {linksAmount} images")

        for num, link in enumerate(links):

            try:
                # download the image
                response = requests.get(link)
                response.raise_for_status()

                # get the first part of the link which will be used as the name of the file
                extractedName = link.split("?")[0]
                filename = os.path.join(
                    tempImageFolder, os.path.basename(extractedName)
                )

                with open(filename, "wb") as file:
                    file.write(response.content)

            except requests.exceptions.RequestException as e:
                print(f"Error downloading {link}: {e}")

            # respond with the progress
            await websocket.send_text(str(num))  # TODO: improve this

        # zip the folder containing all the downloaded images
        responseZipFile = f"{tempImageFolder}.zip"
        zipFolder(responseZipFile, tempImageFolder)

        # delete the folder containing the images
        deleteFolder(tempImageFolder)

        await websocket.close()
        break


@router.post("/auth/create-user", response_class=HTMLResponse)
async def create_user(request: Request):

    form = await request.form()

    # extract fields from the sign up form
    email = form.get("email", "").lower().strip()
    password = form.get("password", "").strip()
    confirm_password = form.get("confirm_password", "").strip()

    # initalise auth settings
    auth = Auth(service="supabase")

    user = None  # user object if registration is successful
    error: str = None  # error message if registration fails
    response: HTMLResponse = None  # response object

    try:
        user = auth.signup(email, password, confirm_password)
    except Exception as exception:
        error = exception

    if error is not None:
        response = HTMLResponse(
            content=f"""<p id="errors" class="col-span-6 text-red-500">{error}</p>""",
            status_code=400,
        )

    if user is not None and error is None:
        response = HTMLResponse()

        response.status_code = 303
        response.headers.update({"HX-Redirect": "/home"})

        response.set_cookie(
            key=JWT,
            value=user.session.access_token,
            expires=user.session.expires_in,
            secure=True,
            httponly=True,
        )

        response.set_cookie(
            key=JWT_TTL,
            value=user.session.expires_in,
            expires=user.session.expires_in,
            secure=True,
            httponly=False,
        )

    return response


@router.post("/auth/sign-user")
async def sign_user(request: Request):

    form = await request.form()

    # extract fields from the sign up form
    email = form.get("email", "").lower().strip()
    password = form.get("password", "").strip()

    # initalise auth settings
    auth = Auth(service="supabase")

    user = None  # user object if sign in is successful
    error: str = None
    response: HTMLResponse = None

    try:
        user = auth.login(email, password)
    except Exception as exception:
        error = exception

    if error is not None:
        response = HTMLResponse(
            content=f"""<p id="errors" class="col-span-6 text-red-500">{error}</p>""",
            status_code=400,
        )

    if user is not None and error is None:
        response = HTMLResponse()

        response.status_code = 303
        response.headers.update({"HX-Redirect": "/home"})

        response.set_cookie(
            key=JWT,
            value=user.session.access_token,
            expires=user.session.expires_in,
            secure=True,
            httponly=True,
        )

        response.set_cookie(
            key=JWT_TTL,
            value=user.session.expires_in,
            expires=user.session.expires_in,
            secure=True,
            httponly=False,
        )

    return response


@router.get("/auth/logout")
def logout():

    response = RedirectResponse(url=LoggedOutRedirect)

    response.delete_cookie(key=JWT)
    response.delete_cookie(key=JWT_TTL)

    return response
