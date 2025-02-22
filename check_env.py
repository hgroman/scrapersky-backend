"""Check environment variables for database connection."""
import os
from dotenv import load_dotenv

load_dotenv()

# Variables to check
variables = [
    'SUPABASE_POOLER_HOST',
    'SUPABASE_POOLER_PORT',
    'SUPABASE_POOLER_USER',
    'SUPABASE_DB_PASSWORD'
]

print("Environment Variable Check:")
print("-" * 50)

for var in variables:
    value = os.getenv(var)
    status = "✅ Set" if value else "❌ Missing"
    print(f"{var}: {status}")
    if value:
        # Show first few chars of password, full value for others
        if 'PASSWORD' in var:
            print(f"  Value: {value[:3]}{'*' * (len(value)-3)}")
        else:
            print(f"  Value: {value}")

print("-" * 50)
