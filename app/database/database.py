from app.models.supabase import Supabase


class Database:

    def __init__(self):

        self.database = Supabase()

    def insert(self, table: str, data: dict):

        return self.database.insert(table, data)
