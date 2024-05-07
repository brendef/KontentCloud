import os
import requests


class Instagram:

    ClientId = os.getenv("INSTAGRAM_CLIENT_ID")
    ClientSecret = os.getenv("INSTAGRAM_SECRET")

    ApiInstagram = "https://api.instagram.com/oauth/access_token"
    GraphInstagram = "https://graph.instagram.com/access_token"

    def __init__(self, url, code):
        self.RedirectUri = url
        self.code: str = code

    def get_token(self):

        url = self.ApiInstagram
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

        url = self.GraphInstagram
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": self.ClientSecret,
            "access_token": shortToken,
        }

        response = requests.get(url, params=params)
        longToken = response.json()["access_token"]
        ttl = response.json()["expires_in"]

        return dict(longToken=longToken, ttl=ttl)
