import sqlite3
from backend import Backend

class SqliteBackend(Backend):
    def __init__(self, dbname):
        self.dbname = dbname

    def addTimeTestResult(self, title, info):
        pass

