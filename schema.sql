-- ============================================================
--  Vehicle Service Management System — Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS vehicle_service_db;
USE vehicle_service_db;

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    phone         VARCHAR(20)  NOT NULL,
    email         VARCHAR(100),
    address       TEXT,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id    INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT NOT NULL,
    make          VARCHAR(50)  NOT NULL,
    model         VARCHAR(50)  NOT NULL,
    year          YEAR         NOT NULL,
    license_plate VARCHAR(20)  NOT NULL UNIQUE,
    color         VARCHAR(30),
    vin           VARCHAR(50),
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Mechanics
CREATE TABLE IF NOT EXISTS mechanics (
    mechanic_id    INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    phone          VARCHAR(20),
    specialization VARCHAR(100),
    status         ENUM('available','busy','off') DEFAULT 'available',
    hired_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Service Catalog
CREATE TABLE IF NOT EXISTS services (
    service_id     INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    description    TEXT,
    price          DECIMAL(10,2) NOT NULL,
    duration_hours DECIMAL(4,1)  DEFAULT 1.0
);

-- Service Orders
CREATE TABLE IF NOT EXISTS service_orders (
    order_id     INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id   INT NOT NULL,
    customer_id  INT NOT NULL,
    mechanic_id  INT,
    status       ENUM('pending','in_progress','completed','cancelled') DEFAULT 'pending',
    notes        TEXT,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (vehicle_id)  REFERENCES vehicles(vehicle_id)  ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(mechanic_id) ON DELETE SET NULL
);

-- Order → Services (many-to-many)
CREATE TABLE IF NOT EXISTS order_services (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT NOT NULL,
    service_id INT NOT NULL,
    price      DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES service_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(service_id)     ON DELETE CASCADE
);

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    order_id       INT NOT NULL,
    amount         DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash','card','upi','bank_transfer') DEFAULT 'cash',
    status         ENUM('paid','pending','failed') DEFAULT 'paid',
    payment_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES service_orders(order_id) ON DELETE CASCADE
);

-- ============================================================
--  Sample Seed Data
-- ============================================================

INSERT INTO customers (name, phone, email, address) VALUES
('Rahul Sharma',    '9876543210', 'rahul@email.com',   '12 MG Road, Bangalore'),
('Priya Mehta',     '9812345678', 'priya@email.com',   '45 Anna Nagar, Chennai'),
('Amit Verma',      '9901234567', 'amit@email.com',    '78 Connaught Place, Delhi'),
('Sunita Rao',      '9823456789', 'sunita@email.com',  '22 Banjara Hills, Hyderabad'),
('Kiran Patil',     '9934567890', 'kiran@email.com',   '9 FC Road, Pune');

INSERT INTO vehicles (customer_id, make, model, year, license_plate, color, vin) VALUES
(1, 'Maruti', 'Swift',      2021, 'KA-01-AB-1234', 'Red',    'MA3FJEB1S00101234'),
(1, 'Honda',  'City',       2019, 'KA-02-CD-5678', 'Silver', 'MAKGE6580KA005678'),
(2, 'Hyundai','Creta',      2022, 'TN-07-EF-9012', 'White',  'MALC241CLNM009012'),
(3, 'Toyota', 'Innova',     2020, 'DL-05-GH-3456', 'Grey',   'MBJBA3BA8L0003456'),
(4, 'Tata',   'Nexon',      2023, 'TS-09-IJ-7890', 'Blue',   'MAT612921N1007890'),
(5, 'Mahindra','XUV700',    2022, 'MH-12-KL-2345', 'Black',  'MA1YC2HMXN8002345');

INSERT INTO mechanics (name, phone, specialization, status) VALUES
('Raju Nair',    '9811122233', 'Engine & Transmission', 'available'),
('Vikram Singh', '9822233344', 'Electrical & AC',       'available'),
('Mohan Das',    '9833344455', 'Body & Paint',          'busy'),
('Suresh Kumar', '9844455566', 'Tyres & Suspension',    'available'),
('Arun Pillai',  '9855566677', 'General Service',       'available');

INSERT INTO services (name, description, price, duration_hours) VALUES
('Oil Change',          'Engine oil & filter replacement',           599.00, 0.5),
('Tyre Rotation',       'Rotate all four tyres for even wear',       499.00, 0.5),
('Brake Inspection',    'Inspect and adjust brake pads/discs',       799.00, 1.0),
('AC Service',          'AC gas recharge and filter cleaning',      1499.00, 2.0),
('Full Service',        'Comprehensive 35-point vehicle check',     2999.00, 4.0),
('Wheel Alignment',     'Computer-aided wheel alignment',            899.00, 1.0),
('Battery Replacement', 'Check and replace car battery',           2499.00, 0.5),
('Engine Tune-up',      'Spark plugs, air filter, fuel filter',    1999.00, 2.5),
('Denting & Painting',  'Minor dent removal and paint touch-up',   4999.00, 8.0),
('Windshield Repair',   'Crack/chip repair or full replacement',   3499.00, 3.0);

INSERT INTO mechanics (name, phone, specialization, status) VALUES
('Demo Tech', '0000000000', 'General', 'available');

INSERT INTO service_orders (vehicle_id, customer_id, mechanic_id, status, notes, total_amount, created_at) VALUES
(1, 1, 1, 'completed', 'Regular maintenance', 3598.00, DATE_SUB(NOW(), INTERVAL 10 DAY)),
(3, 2, 2, 'in_progress','AC not cooling properly', 1499.00, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(4, 3, 4, 'pending',    'Vibration at high speed', 1398.00, NOW()),
(5, 4, 1, 'completed',  'Annual service done',     2999.00, DATE_SUB(NOW(), INTERVAL 20 DAY)),
(6, 5, 5, 'pending',    'Routine checkup',          599.00, NOW());

INSERT INTO order_services (order_id, service_id, price) VALUES
(1, 1, 599.00),(1, 3, 799.00),(1, 6, 899.00),(1, 2, 499.00),(1, 5, 599.00),
(2, 4, 1499.00),
(3, 2, 499.00),(3, 6, 899.00),
(4, 5, 2999.00),
(5, 1, 599.00);

INSERT INTO payments (order_id, amount, payment_method, status, payment_date) VALUES
(1, 3598.00, 'card',  'paid', DATE_SUB(NOW(), INTERVAL 10 DAY)),
(4, 2999.00, 'upi',   'paid', DATE_SUB(NOW(), INTERVAL 20 DAY));
