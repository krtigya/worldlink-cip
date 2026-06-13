import sys
sys.path.insert(0, ".")
from app.db.session import get_sync_db
from sqlalchemy import text

session = next(get_sync_db())

try:
    
    result = session.execute(text("SELECT id, name, price FROM plans WHERE isp_slug = 'worldlink' LIMIT 1")).fetchone()
    
    if result:
        plan_id, name, price = result
        print(f"Found plan: '{name}' with current price: {price}")
        
        
        fake_price = 99999
        session.execute(
            text("UPDATE plans SET price = :price WHERE id = :id"),
            {"price": fake_price, "id": plan_id}
        )
        session.commit()
        print(f"Successfully changed price to {fake_price} to trigger alert tracking.")
    else:
        print("No plans found in the database. Run your seed script or scraper first!")

except Exception as e:
    print(f"Error connecting or executing: {e}")
finally:
    session.close()