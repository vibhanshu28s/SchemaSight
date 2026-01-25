-- Insert data in tables
INSERT INTO departments (name) VALUES
('Engineering'),
('Sales'),
('Marketing'),
('HR'),
('Finance'),
('Operations');

INSERT INTO employees (name, department_id, email, salary) VALUES
('John Smith', 1, 'john.smith@company.com', 85000),
('Sarah Johnson', 1, 'sarah.johnson@company.com', 92000),
('Mike Davis', 2, 'mike.davis@company.com', 65000),
('Emily Brown', 2, 'emily.brown@company.com', 68000),
('David Wilson', 3, 'david.wilson@company.com', 72000),
('Lisa Anderson', 3, 'lisa.anderson@company.com', 70000),
('James Taylor', 4, 'james.taylor@company.com', 55000),
('Jennifer Martinez', 4, 'jennifer.martinez@company.com', 58000),
('Robert Thomas', 5, 'robert.thomas@company.com', 78000),
('Mary Garcia', 5, 'mary.garcia@company.com', 75000),
('William Rodriguez', 6, 'william.rodriguez@company.com', 62000),
('Patricia Lee', 6, 'patricia.lee@company.com', 64000);

INSERT INTO products (name, price) VALUES
('Laptop Pro 15', 1299.99),
('Wireless Mouse', 29.99),
('Mechanical Keyboard', 149.99),
('USB-C Hub', 79.99),
('Monitor 27 inch', 399.99),
('Webcam HD', 89.99),
('Headphones Noise Cancelling', 249.99),
('Desk Lamp LED', 45.99),
('Ergonomic Chair', 599.99),
('Standing Desk', 799.99),
('Phone Case', 19.99),
('Portable Charger', 39.99),
('HDMI Cable', 12.99),
('External SSD 1TB', 159.99),
('Bluetooth Speaker', 129.99);

INSERT INTO orders (customer_name, employee_id, order_total, order_date) VALUES
('Acme Corporation', 3, 2599.98, '2024-01-15'),
('Tech Startup Inc', 3, 1599.97, '2024-01-18'),
('Global Solutions Ltd', 4, 899.97, '2024-01-20'),
('Innovate Co', 4, 3499.95, '2024-01-22'),
('Digital Ventures', 3, 549.98, '2024-01-25'),
('Smart Systems', 4, 1299.99, '2024-01-28'),
('Future Tech LLC', 3, 2199.96, '2024-02-01'),
('Cloud Nine Inc', 4, 799.98, '2024-02-05'),
('Data Dynamics', 3, 4599.93, '2024-02-10'),
('Quantum Corp', 4, 679.97, '2024-02-12'),
('Nexus Industries', 3, 1849.96, '2024-02-15'),
('Apex Solutions', 4, 949.98, '2024-02-18'),
('Zenith Company', 3, 3299.94, '2024-02-20'),
('Omega Enterprises', 4, 1599.97, '2024-02-22'),
('Alpha Tech', 3, 2899.95, '2024-02-25');