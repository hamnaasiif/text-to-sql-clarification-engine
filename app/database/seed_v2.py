import psycopg2
from dotenv import load_dotenv
import os

# to prevent hard coding database url we used .env file
load_dotenv()
db_url = os.getenv("DATABASE_URL")
print("Connecting to:", db_url)
# creates actual connection to database
conn = psycopg2.connect(db_url)

# to execute commands
cur = conn.cursor()

products = [
    ('T-Shirt', 'Clothing', 15.00, 300),
    ('Jeans', 'Clothing', 40.00, 150),
    ('Rice Bag (10kg)', 'Groceries', 20.00, 500),
    ('Novel - Fiction', 'Books', 12.00, 100),
    ('Blender', 'Home Appliances', 60.00, 90),
]

for p in products:
    cur.execute(
        "INSERT INTO products (name, category, price, stock_quantity) VALUES (%s, %s, %s, %s)",
        p
    )

print(f"{len(products)} products inserted.")

orders = [
    (1, '2024-06-10', 40.00, 'completed'),
    (1, '2026-08-05', 60.00, 'completed'),
    (5, '2025-05-12', 30.00, 'completed'),
    (5, '2025-06-18', 30.00, 'completed'),
    (5, '2026-08-20', 30.00, 'completed'),
    (3, '2024-09-01', 500.00, 'cancelled'),
    (2, '2026-08-12', 40.00, 'pending'),
]

order_ids = []
for o in orders:
    cur.execute(
        "INSERT INTO orders (customer_id, order_date, total_amount, order_status) VALUES (%s, %s, %s, %s) RETURNING order_id",
        o
    )
    order_ids.append(cur.fetchone()[0])

print(f"{len(orders)} orders inserted. New order_ids: {order_ids}")

# order_items — naye orders ke products
order_items = [
    (order_ids[0], 12, 1, 40.00),
    (order_ids[1], 15, 1, 60.00),
    (order_ids[2], 11, 2, 15.00),
    (order_ids[3], 11, 2, 15.00),
    (order_ids[4], 11, 2, 15.00),
    (order_ids[5], 6, 1, 500.00),
    (order_ids[6], 12, 1, 40.00),
]

for oi in order_items:
    cur.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
        oi
    )

print(f"{len(order_items)} order_items inserted.")

# payments — har order ka payment record
payments = [
    (order_ids[0], 40.00, 'Credit Card', '2024-06-10', 'completed'),
    (order_ids[1], 60.00, 'Cash', '2026-08-05', 'completed'),
    (order_ids[2], 30.00, 'Debit Card', '2025-05-12', 'completed'),
    (order_ids[3], 30.00, 'Cash', '2025-06-18', 'completed'),
    (order_ids[4], 30.00, 'Credit Card', '2026-08-20', 'completed'),
    (order_ids[5], 500.00, 'Credit Card', '2024-09-01', 'refunded'),
    (order_ids[6], 40.00, 'Debit Card', '2026-08-12', 'pending'),
]

for pay in payments:
    cur.execute(
        "INSERT INTO payments (order_id, amount, payment_method, payment_date, payment_status) VALUES (%s, %s, %s, %s, %s)",
        pay
    )

print(f"{len(payments)} payments inserted.")
# to save changes permanently
conn.commit()

# closing connection
cur.close()
conn.close()