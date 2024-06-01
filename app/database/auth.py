SUPABASE = "supabase"


class Auth:

    auth = None

    def __init__(self, **kwargs):

        service: str = None

        if "service" in kwargs.keys():
            service = kwargs["service"]

        if service is None:
            print("Auth Service is None")
            return None

        # this is dynamic, can add more services here
        if service == SUPABASE:
            from models.supabase import Supabase

            self.auth = Supabase()

    def login(self, email: str, password: str):
        return self.auth.login(email, password)

    def signup(self, email: str, password: str):
        return self.auth.signup(email, password)

    def logout(self):
        pass

    def reset_password(self, email: str):
        pass
