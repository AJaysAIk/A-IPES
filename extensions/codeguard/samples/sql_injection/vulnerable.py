"""Text-only fixture: untrusted input interpolated into a query."""


def lookup(connection, username: str):
    return connection.execute(f"SELECT display_name FROM demo_users WHERE name = '{username}'")
