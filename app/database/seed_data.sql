INSERT INTO customers(name, email, signup_date) VALUES
('Ahmed Khan', 'ahmed.khan@email.com', '2024-01-15'),
('Ayesha Malik', 'ayesha.malik@email.com', '2024-02-10'),
('Bilal Ahmed', 'bilal.ahmed@email.com', '2024-03-05'),
('Sara Farooq', 'sara.farooq@email.com', '2024-01-28'),
('Hamna Asif','hamna.asif@gmail.com','2025-01-23'),
('Yumna Khan', 'yumna.khan@gmail.com','2023-08-12'),
('Ali Rehman','ali.rehman@yahoo.com','2023-10-12'),
('Noor Fatima','noor.fatima@hotmail.com','2024-03-04'),
('Hania Noor','hania.noor@gmail.com','2023-03-15');

INSERT INTO products(name, category, price, stock_quantity) VALUES
('Laptop', 'Electronics', 1200.00, 50),
('Mobile', 'Electronics', 800.00, 100),
('Tablet', 'Electronics', 300.00, 75),
('Monitor', 'Electronics', 200.00, 60),
('Keyboard', 'Electronics', 50.00, 200),
('Mouse', 'Electronics', 25.00, 250),
('Headphones', 'Electronics', 100.00, 150),
('Speaker', 'Electronics', 75.00, 120),
('Printer', 'Electronics', 150.00, 80),
('Camera', 'Electronics', 500.00, 40);

INSERT INTO orders(customer_id, order_date, total_amount, order_status) VALUES
(1, '2024-01-15', 1200.00, 'completed'),
(2, '2024-02-10', 800.00, 'completed'),
(3, '2024-03-05', 300.00, 'completed'),
(4, '2024-01-28', 200.00, 'completed'),
(5, '2025-01-23', 150.00, 'completed'),
(6, '2023-08-12', 100.00, 'completed'),
(7, '2023-10-12', 75.00, 'completed'),
(8, '2024-03-04', 50.00, 'completed'),
(9, '2023-03-15', 25.00, 'completed');

INSERT INTO order_items(order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1200.00),
(2, 2, 1, 800.00),
(3, 3, 1, 300.00),
(4, 4, 1, 200.00),
(5, 5, 1, 150.00),
(6, 6, 1, 100.00),
(7, 7, 1, 75.00),
(8, 8, 1, 50.00),
(9, 9, 1, 25.00);

INSERT INTO payments(order_id, amount, payment_method, payment_date, payment_status) VALUES
(1, 1200.00, 'Credit Card', '2024-01-15', 'completed'),
(2, 800.00, 'Debit Card', '2024-02-10', 'completed'),
(3, 300.00, 'Cash', '2024-03-05', 'completed'),
(4, 200.00, 'Credit Card', '2024-01-28', 'completed'),
(5, 150.00, 'Debit Card', '2025-01-23', 'completed'),
(6, 100.00, 'Cash', '2023-08-12', 'completed'),
(7, 75.00, 'Credit Card', '2023-10-12', 'completed'),
(8, 50.00, 'Debit Card', '2024-03-04', 'completed'),
(9, 25.00, 'Cash', '2023-03-15', 'completed');