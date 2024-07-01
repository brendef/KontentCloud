from app.models.supabase import Supabase


class Database:

    def __init__(self):

        self.database = Supabase()

    def insert(self, table: str, data: dict):

        return self.database.insert(table, data)

    def delete_single(self, table: str, column: str, where: str):

        return self.database.delete_single(table, column, where)

    def delete_user(self, user_id: str):

        return self.delete_single("Users", "id", user_id)

    def select(self, table: str, columns: str, where: dict, count: str = None):

        return self.database.select(table, columns, where, count)
