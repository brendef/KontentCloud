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

        try:
            user = self.supabase.auth.sign_up(credentials)
        except Exception as e:
            raise Exception(e)

        return user

    def login(self, email: str, password: str):

        # supabase function
        credentials = {"email": email, "password": password}

        try:
            user = self.supabase.auth.sign_in_with_password(credentials)
        except Exception as e:
            raise Exception(e)

        return user

    def getuser(self, token: str):

        try:
            user = self.supabase.auth.get_user(token)
        except Exception as e:
            raise Exception(e)

        return user

    def insert(self, table: str, data: dict):

        try:

            response, count = self.supabase.table(table).insert(data).execute()
            print(count)

        except Exception as e:
            raise Exception(e)

        return response
