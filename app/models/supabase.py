import os

from supabase import create_client, Client


class Supabase:

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

    supabase: Client = None

    def __init__(self):

        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)

    def signup(self, email: str, password: str):

        # pass the email and password to the supabase function as credentials dictionary
        credentials = {"email": email, "password": password}
        user = self.supabase.auth.sign_up(credentials)

        return user

    def login(self, email: str, password: str):

        # supabase function
        user = self.supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        return user
