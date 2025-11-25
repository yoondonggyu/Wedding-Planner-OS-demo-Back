from app.core.database import engine, Base
from app.models.db import User, Post, Comment, PostLike, Tag

# Create all tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")


