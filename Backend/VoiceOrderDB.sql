CREATE DATABASE voice_orders;

USE voice_orders;

CREATE TABLE IF NOT EXISTS orders  (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending'
);
