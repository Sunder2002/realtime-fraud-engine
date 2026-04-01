import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://admin:password123@localhost:5432/fraud_db")

print("📊 Querying Live Database Records...")
try:
    with engine.connect() as conn:
        # Check total counts
        df = pd.read_sql(text("SELECT status, count(*) as count FROM transactions GROUP BY status"), conn)
        
        if df.empty:
            print("📭 Database is still empty. Make sure the API is running and printing 'Saved to DB ✅'!")
        else:
            print("\n--- SENTINEL DATABASE STATS ---")
            print(df.to_string(index=False))
            
            # Show the last 5 transactions
            print("\n--- LATEST 5 ENTRIES ---")
            latest = pd.read_sql(text("SELECT amount, status, probability FROM transactions ORDER BY id DESC LIMIT 5"), conn)
            print(latest.to_string(index=False))
except Exception as e:
    print(f"❌ Error: {e}")