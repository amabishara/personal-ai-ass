from modules.database import engine, Base
import modules.models  # This is crucial! It forces Python to read your tables.

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database created successfully! You should see database.db in your folder.")