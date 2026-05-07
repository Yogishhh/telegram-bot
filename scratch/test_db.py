import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from database.db import get_analytics, init_db

try:
    init_db()
    print("Database initialized.")
    stats = get_analytics()
    print(f"Stats: {stats}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
