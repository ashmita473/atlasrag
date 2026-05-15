import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from db.models import Base
from db.session import engine

Base.metadata.create_all(bind=engine)

print("Database initialized successfully.")