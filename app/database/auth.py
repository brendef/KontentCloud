from app.lib.auth import validate_email, validate_password

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
            from app.models.supabase import Supabase

            self.auth = Supabase()

    def login(self, email: str, password: str):

        if (emailMessage := validate_email(email)) and len(emailMessage) > 0:
            raise Exception(f"Invalid email: {emailMessage}")

        if (passwordMessage := validate_password(password)) and len(
            passwordMessage
        ) > 0:
            raise Exception(f"Invalid password: {passwordMessage}")

        return self.auth.login(email, password)

    def signup(self, email: str, password: str, confirm_password: str):

        if confirm_password != password:
            raise Exception("Passwords do not match")

        if (emailMessage := validate_email(email)) and len(emailMessage) > 0:
            raise Exception(f"Invalid email: {emailMessage}")

        if (passwordMessage := validate_password(password)) and len(
            passwordMessage
        ) > 0:
            raise Exception(f"Invalid password: {passwordMessage}")

        return self.auth.signup(email, password)

    def logout(self, token: str):
        try:
            response = self.auth.sign_out_with_token(token)
        except Exception as e:
            raise Exception(e)

        return response

    def reset_password(self, email: str):
        pass
