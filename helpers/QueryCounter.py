from django.db import connection


class QueryCounter:

    def __init__(self):
        self.counter = len(connection.queries)
        self.index = 1
        print("Current Count: ", self.counter)

    def reset(self):
        self.counter = len(connection.queries)
        self.index = 1

    def print(self):
        print(self.index, ':', len(connection.queries) - self.counter)
        self.index += 1
