from app.database.session import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS gst_number VARCHAR;'))
        conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS gst_status VARCHAR DEFAULT \'Verification Pending\';'))
        conn.execute(text('ALTER TABLE "stock_lot" ADD COLUMN IF NOT EXISTS cultivation_record_id INTEGER REFERENCES crop_cultivation_record(id);'))
        conn.execute(text('ALTER TABLE "stock_lot" ADD COLUMN IF NOT EXISTS quality_cert_filename VARCHAR;'))
        conn.execute(text('ALTER TABLE "stock_lot" ADD COLUMN IF NOT EXISTS quality_cert_url VARCHAR;'))
        conn.execute(text('ALTER TABLE "stock_lot" ADD COLUMN IF NOT EXISTS quality_cert_uploaded_at TIMESTAMP;'))
        conn.execute(text('ALTER TABLE "trade_order" ADD COLUMN IF NOT EXISTS bid_id INTEGER REFERENCES bid(id);'))
        conn.execute(text('ALTER TABLE "trade_order" ADD COLUMN IF NOT EXISTS future_crop_lot_id INTEGER REFERENCES future_crop_lot(id);'))
        conn.execute(text('ALTER TABLE "trade_order" ALTER COLUMN stock_bid_id DROP NOT NULL;'))
        conn.execute(text('ALTER TABLE "trade_order" ALTER COLUMN stock_lot_id DROP NOT NULL;'))
        conn.commit()
    print("PostgreSQL migration executed successfully.")

if __name__ == "__main__":
    migrate()
