SUPABASE = "supabase"


class Database:

    def __init__(self, **kwargs):

        service: str = None

        if "service" in kwargs.keys():
            service = kwargs["service"]

        if service is None:
            print("Database Service is None")
            return None

        # this is dynamic, can add more services here
        if service == SUPABASE:
            from models.supabase import Supabase

            self.database = Supabase()

        return self.database
