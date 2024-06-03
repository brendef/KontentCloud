import os
import requests


class Instagram:

    CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
    CLIENT_SECRET = os.getenv("INSTAGRAM_SECRET")

    API_INSTAGRAM_URL = "https://api.instagram.com/oauth/access_token"
    GRAPH_INSTAGRAM_URL = "https://graph.instagram.com/access_token"
    GRAPH_MEDIA_URL = "https://graph.instagram.com/me/media"
    GRAPH_USER_URL = "https://graph.instagram.com/me"

    def __init__(self, **kwargs):

        if "token" in kwargs.keys():
            self.token = kwargs["token"]

        if "code" in kwargs.keys():
            self.code = kwargs["code"]

        if "redirectUri" in kwargs.keys():
            self.RedirectUri = kwargs["redirectUri"]

    def get_token(self):

        url = self.API_INSTAGRAM_URL
        payload = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": self.RedirectUri,
            "code": self.code,
        }

        response = requests.post(url, data=payload)

        print(response.json())

        shortToken = response.json()["access_token"]

        return shortToken

    # exchanges the short token for a long lived token.
    def exchange_token(self, shortToken: str):

        if shortToken is None:
            print("Short token is None")
            return None

        url = self.GRAPH_INSTAGRAM_URL
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": self.CLIENT_SECRET,
            "access_token": shortToken,
        }

        response = requests.get(url, params=params)
        longToken = response.json()["access_token"]
        ttl = response.json()["expires_in"]

        return dict(longToken=longToken, ttl=ttl)

    def get_user(self):

        url = self.GRAPH_USER_URL
        params = {
            "fields": "id,username,account_type,media_count",
            "access_token": self.token,
        }

        response = requests.get(url, params=params)
        user = response.json()

        return user

    def get_feed(self):

        url = self.GRAPH_MEDIA_URL
        params = {
            "fields": "id,username,media_type,media_url,caption",
            "access_token": self.token,
        }

        response = requests.get(url, params=params)
        feed = response.json()

        return feed

    def get_next_feed(self, url: str):

        response = requests.get(url)
        feed = response.json()

        return feed
