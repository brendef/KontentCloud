import json, requests, os, urllib

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, WebSocket, BackgroundTasks, Header
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel


from app.models.facebook import Instagram
from app.lib.io import createFolder, zipFolder, deleteFolder

from app.database.auth import Auth
from app.database.database import Database

router = APIRouter()  # init app router
templates = Jinja2Templates(directory="app/templates")  # load html templates

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

    env = os.getenv("ENV")
    baseUrl = os.getenv(f"BASE_URL_{env}")
    redirectUri = f"https://{baseUrl}/authorise-instagram/"

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

    env = os.getenv("ENV")
    baseUrl = os.getenv(f"BASE_URL_{env}")

    context = {"instagram_auth": False, "redirectBase": baseUrl}

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)
    if cookieLongToken is not None:
        context["instagram_auth"] = True

    return templates.TemplateResponse(
        request=request, name="pages/home.html", context=context
    )


# display the users instagram feed, once authenticated
@router.get("/instagram-feed")
def feed_template(request: Request):

    serverType = os.getenv("SERVER_TYPE")

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)

    instagram = Instagram(token=cookieLongToken)
    user = instagram.get_user()
    feed = instagram.get_feed()

    return templates.TemplateResponse(
        request=request,
        name="pages/instagram-feed.html",
        context={"user": user, "feed": feed, "serverType": serverType},
    )


@router.get("/get-instagram-feed")
def feed_htmx(request: Request, nextUrl: str):

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)

    instagram = Instagram(token=cookieLongToken)
    feed = instagram.get_next_feed(nextUrl)

    htmlResponse = ""

    for image in feed["data"]:

        if image["media_type"] == "CAROUSEL_ALBUM":
            htmlResponse += f"""
             <div id="{image["id"]}" hx-get="/get-carousel-album/{image["id"]}" class="image border border-gray-200"
                hx-swap="outerHTML" hx-indicator="#carousel-loader-{image["id"]}">
                <p class="carousel-album-text absolute bg-black text-white px-2">album</p>
                <img class="thumbnail carousel" src="{image["media_url"]}" alt="" />
            </div>
            <div id="carousel-loader-{image["id"]}" class="loader-class htmx-indicator" hidden>
                <div role="status">
                    <svg class="inline w-8 h-8 text-gray-200 animate-spin fill-blue-600"
                        viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                            fill="currentColor" />
                        <path
                            d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                            fill="currentFill" />
                    </svg>
                    <span class="sr-only">Loading...</span>
                </div>
                <p>Loading album...</p>
            </div>

            <script>
                document.getElementById("{image["id"]}").addEventListener('htmx:beforeRequest', function (evt) {{
                
                    let id = evt.srcElement.id

                    const loadingIndicator = document.querySelector("#carousel-loader-{image["id"]}");
                    let src = document.getElementById(evt.srcElement.id).querySelector(".thumbnail").src
                    selectedImages = selectedImages.filter(item => item != src)

                    if (loadingIndicator) {{
                        loadingIndicator.style.display = 'block';
                    }}

                }});

                document.getElementById("{image["id"]}").addEventListener('htmx:afterRequest', function (evt) {{

                    let id = evt.srcElement.id 
                    let src = evt.srcElement.querySelector(".thumbnail").src
                    selectedImages = selectedImages.filter(item => item != src)
                    const loadingIndicator = document.querySelector("#carousel-loader-{image["id"]}");
                    if (loadingIndicator) {{
                        loadingIndicator.style.display = 'none';
                    }}

                }});
            </script>
        """

        if image["media_type"] == "VIDEO":

            htmlResponse += f"""
            <div id="{ image["id"] }" class="image border border-gray-200">
                <video id="{image["id"]}" class="thumbnail aspect-square" width="500" height="100">
                    <source src="{image["media_url"]}#t=0.1" type="video/mp4">
                    Your browser does not support the video tag.
                </video> 
            </div>

            <script>
                document.getElementById('select-all-box').checked = false;
            </script>
        """

        if image["media_type"] == "IMAGE":
            htmlResponse += f"""
            <div id="{image["id"]}" class="image border border-gray-200"> <img class="thumbnail" src="{image["media_url"]}" alt="" /> </div>
        """

        htmlResponse += f"""
            <script>
                document.getElementById("{image["id"]}").addEventListener('click', (e) => {{
                    selectImage(e.srcElement.src, e.target, "{image["id"]}")
                }})

            </script>

            <script>
                document.getElementById('select-all-box').checked = false;
            </script>
        """

    if "next" in feed["paging"]:
        htmlResponse += f"""<div id="loading-spinner" hx-get="/get-instagram-feed" hx-vars="{{ 'nextUrl':'{feed["paging"]["next"]}' }}" hx-trigger="revealed" hx-swap="outerHTML">
            <div class="text-center">
                <div role="status">
                    <svg aria-hidden="true" class="inline w-8 h-8 text-gray-200 animate-spin fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
                        <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
                    </svg>
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
        </div>
    """

    return HTMLResponse(content=htmlResponse)


@router.get("/get-carousel-album/{media_id}")
def carousel_album_htmx(request: Request, media_id: str):

    # get the cookie from the request
    cookieLongToken = request.cookies.get(LONG_TOKEN)

    instagram = Instagram(token=cookieLongToken)

    try:
        media = instagram.get_media(media_id)
    except Exception as e:
        print(e)
        return HTMLResponse(content="An error occured")

    htmlResponse = ""
    for child in media["children"]["data"]:
        id = child["id"]
        childImage = instagram.get_child_media(id)

        htmlResponse += f"""
            <div id="{childImage["id"]}" class="image border border-gray-200">
                <img class="thumbnail" src="{childImage["media_url"]}" alt="" />
            </div>

            <script>
                document.getElementById("{childImage["id"]}").addEventListener('click', (e) => {{
                    selectImage(e.srcElement.src, e.target, "{childImage["id"]}")
                }})
            </script>
        """

    return HTMLResponse(content=htmlResponse)


# Websocket route


@router.get("/download-zip")
def download_zip(request: Request, background_tasks: BackgroundTasks):

    userLongToken = request.cookies.get(LONG_TOKEN)
    zipFileLocation = f"/tmp/{userLongToken}.zip"

    background_tasks.add_task(os.remove, zipFileLocation)

    return FileResponse(path=zipFileLocation, filename="instagram_images.zip")


@router.websocket("/download-images/ws")
async def download_images_ws(websocket: WebSocket):

    print("start /download-images/ws route")

    print("Websocket connection opened")
    await websocket.accept()

    userLongToken = websocket.cookies.get(LONG_TOKEN)

    serverType = os.getenv("SERVER_TYPE")

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

        tempImageFolder = f"/tmp/{userLongToken}"
        createFolder(tempImageFolder)

        # notify the client that the download is starting and how many images are being downloaded
        await websocket.send_text(f"Downloading {linksAmount} images")

        for num, link in enumerate(links):

            filename: str = None

            # download the image
            response = requests.get(url=link, stream=True)

            # get the first part of the link which will be used as the name of the file
            extractedName = link.split("?")[0]
            filename = os.path.join(tempImageFolder, os.path.basename(extractedName))

            # there is no file extension in video links
            if not ".jpg" in filename:
                filename += ".mp4"

            with open(filename, "wb") as file:
                file.write(response.content)

            # respond with the progress
            await websocket.send_text(json.dumps({"total": len(links), "count": num}))

        # zip the folder containing all the downloaded images
        responseZipFile = f"{tempImageFolder}.zip"
        zipFolder(responseZipFile, tempImageFolder)

        # delete the folder containing the images
        deleteFolder(tempImageFolder)

        await websocket.close()
        break


@router.get("/download-images")
async def download_images(
    request: Request, linksStr: str = None, response: FileResponse = None
):

    print("start: /download-images route")

    userLongToken = request.cookies.get(LONG_TOKEN)

    if linksStr is None:
        return

    print(linksStr)

    links = linksStr.split(",")

    print("downloading", links)

    tempImageFolder = f"/tmp/{userLongToken}"
    createFolder(tempImageFolder)

    for link in links:

        filename: str = None

        # download the image
        response = requests.get(url=link, stream=True)

        # get the first part of the link which will be used as the name of the file
        extractedName = link.split("?")[0]
        filename = os.path.join(tempImageFolder, os.path.basename(extractedName))

        # there is no file extension in video links
        if not ".jpg" in filename:
            filename += ".mp4"

        with open(filename, "wb") as file:
            file.write(response.content)

    # zip the folder containing all the downloaded images
    responseZipFile = f"{tempImageFolder}.zip"
    zipFolder(responseZipFile, tempImageFolder)

    # delete the folder containing the images
    deleteFolder(tempImageFolder)

    file = download_zip(request, BackgroundTasks())

    return file


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


@router.post("/join-waiting")
async def join_waiting_htmx(request: Request):

    database = Database()

    form = await request.form()
    email = form.get("email", "").lower().strip()

    ipAddress = request.client.host

    if email == "" or "@" not in email or "." not in email:
        return HTMLResponse(
            content="""<p class="flex text-center text-red-500">Please enter a valid email address</p>"""
        )

    try:
        database.insert(
            "waiting_list", {"email_address": email, "ip_address": ipAddress}
        )
    except Exception as e:
        print(e)
        return HTMLResponse(
            content="""<p class="text-center text-red-500">You already seem to be on the waiting list</p>"""
        )

    return HTMLResponse(
        content="""<p class="text-center text-green-500">Great! You will be notified when we add new features.</p>"""
    )


@router.get("/coming-soon")
def coming_soon(request: Request):
    return templates.TemplateResponse(request=request, name="pages/coming-soon.html")


@router.get("/privacy-policy")
def privacy_policy(request: Request):
    return templates.TemplateResponse(request=request, name="pages/privacy-policy.html")


@router.get("/tos")
def terms_and_conditions(request: Request):
    return templates.TemplateResponse(request=request, name="pages/tos.html")


@router.get("/profile")
async def user_profile_template(request: Request):

    context = dict()

    # get the cookie from the request
    jwt = request.cookies.get(JWT)

    auth = Auth(service="supabase")
    user = auth.user(jwt)

    if user is None:
        return logout()

    context["user"] = dict(user)

    return templates.TemplateResponse(
        request=request, name="pages/profile.html", context=context
    )


@router.post("/delete-user-data")
async def delete_user_data(request: Request):

    database = Database()

    decoded_str = bytes(await request.body()).decode("utf-8")
    parsed_data = urllib.parse.parse_qs(decoded_str)
    body = {k: v[0] for k, v in parsed_data.items()}

    if not body["email"]:
        return "Something went wrong"

    email = body["email"]

    # delete user data from the waiting list
    database.delete_single("waiting_list", "email_address", email)

    return f"data deleted successfully"


@router.post("/delete-account")
async def delete_account(request: Request):

    jwt = request.cookies.get(JWT)

    auth = Auth(service="supabase")

    try:
        auth.delete_user(jwt)
    except Exception as e:
        print(e)
        return HTMLResponse(
            content="""<p class="text-center text-red-500">An error occured</p>"""
        )

    response = HTMLResponse()
    response.status_code = 303
    response.headers.update({"HX-Redirect": "/"})

    return response


@router.get("/how-to")
def how_to(request: Request):
    return templates.TemplateResponse(request=request, name="pages/how-to.html")
