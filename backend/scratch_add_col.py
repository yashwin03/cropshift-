import app.patch_bcrypt
from app.database.session import engine
from sqlalchemy import text

with engine.connect() as c:
    c.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS partner_code VARCHAR;'))
    c.commit()
    print("partner_code column successfully added to \"user\" table!")
