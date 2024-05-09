import os
import requests


class Instagram:

    ClientId = os.getenv("INSTAGRAM_CLIENT_ID")
    ClientSecret = os.getenv("INSTAGRAM_SECRET")

    ApiInstagramURL = "https://api.instagram.com/oauth/access_token"
    GraphInstagramURL = "https://graph.instagram.com/access_token"
    GraphMediaURL = "https://graph.instagram.com/me/media"
    GraphUserURL = "https://graph.instagram.com/me"

    def __init__(self, **kwargs):

        if "token" in kwargs.keys():
            self.token = kwargs["token"]

        if "code" in kwargs.keys():
            self.code = kwargs["code"]

        if "redirectUri" in kwargs.keys():
            self.RedirectUri = kwargs["redirectUri"]

    def get_token(self):

        url = self.ApiInstagramURL
        payload = {
            "client_id": self.ClientId,
            "client_secret": self.ClientSecret,
            "grant_type": "authorization_code",
            "redirect_uri": self.RedirectUri,
            "code": self.code,
        }

        response = requests.post(url, data=payload)
        shortToken = response.json()["access_token"]

        return shortToken

    # exchanges the short token for a long lived token.
    def exchange_token(self, shortToken: str):

        if shortToken is None:
            print("Short token is None")
            return None

        url = self.GraphInstagramURL
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": self.ClientSecret,
            "access_token": shortToken,
        }

        response = requests.get(url, params=params)
        longToken = response.json()["access_token"]
        ttl = response.json()["expires_in"]

        return dict(longToken=longToken, ttl=ttl)

    def get_user(self):

        url = self.GraphUserURL
        params = {"fields": "id,username", "access_token": self.token}

        response = requests.get(url, params=params)
        user = response.json()

        return user

    def get_feed(self):

        url = self.GraphMediaURL
        params = {
            "fields": "id,username,media_type,media_url,caption",
            "access_token": self.token,
        }

        response = requests.get(url, params=params)
        try:
            feed = response.json()
        except:
            feed = None

        return feed
