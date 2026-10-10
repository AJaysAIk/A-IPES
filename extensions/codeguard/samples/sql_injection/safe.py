"""Parameterized SQLite query; values remain separate from SQL syntax."""


def lookup(connection, username: str):
    return connection.execute("SELECT display_name FROM demo_users WHERE name = ?", (username,))
