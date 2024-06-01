import os

from supabase import create_client, Client


class Supabase:

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

    supabase: Client = None

    def __init__(self):

        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)

    def signup(self, email: str, password: str):

        # TODO: Implement validation
        if email is None or password is None:
            print("Email or Password is None")
            return None

        # TODO: Implement validation
        if len(password) < 8:
            print("Password is too short")
            return None

        # supabase expects the credentials to be in the form of a dictionary
        credentials = {"email": email, "password": password}
        user = self.supabase.auth.sign_up(credentials)

        return user

    def login(self, email: str, password: str):

        # TODO: Implement validation
        if email is None or password is None:
            print("Email or Password is None")
            return None

        # supabase function
        user = self.supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        return user
