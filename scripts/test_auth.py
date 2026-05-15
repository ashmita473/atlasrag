import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from db.session import SessionLocal
from auth.auth_handler import AuthHandler


db = SessionLocal()

auth = AuthHandler()


try:

    user = auth.register(
        db,
        "ashmita",
        "mypassword123"
    )

    print("User registered:")
    print(user.username)

except Exception as e:

    print(f"Register error: {e}")


logged_in = auth.login(
    db,
    "ashmita",
    "mypassword123"
)

if logged_in:

    print("Login successful!")

else:

    print("Login failed.")