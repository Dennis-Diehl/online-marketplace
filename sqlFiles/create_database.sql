
-- Sicherstellen, dass die Foreign Key Constraints keine Probleme verursachen
SET FOREIGN_KEY_CHECKS = 0;

-- Löschen der Tabellen in der richtigen Reihenfolge, um Abhängigkeitsprobleme zu vermeiden
DROP TABLE IF EXISTS Messaging;
DROP TABLE IF EXISTS Subscriptions;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS ShoppingCartItems;
DROP TABLE IF EXISTS ShoppingCarts;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Payments;
DROP TABLE IF EXISTS Sellers;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Pictures;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS PaymentMethods;
DROP TABLE IF EXISTS Visitors;

-- Wiederherstellen der Foreign Key Constraints
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    acc_creation_date DATE DEFAULT CURRENT_DATE,
    cart_id INT,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE Sellers (
    seller_id INT PRIMARY KEY,
    shopname VARCHAR(255) NOT NULL,
    website_url VARCHAR(255),
    rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
    FOREIGN KEY (seller_id) REFERENCES Users(user_id)
);

CREATE TABLE ShoppingCarts (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Pictures (
    pic_id INT PRIMARY KEY AUTO_INCREMENT,
    source VARCHAR(1000) NOT NULL
);

CREATE TABLE Category (
    c_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    superiorc_id INT DEFAULT NULL,
    FOREIGN KEY (superiorc_id) REFERENCES Category(c_id)
);

CREATE TABLE Products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    picture_id INT,
    cost DECIMAL(10, 2) NOT NULL CHECK (cost >= 0),
    available_copies INT NOT NULL CHECK (available_copies >= 0),
    category_id INT,
    information TEXT,
    seller_id INT,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (picture_id) REFERENCES Pictures(pic_id),
    FOREIGN KEY (category_id) REFERENCES Category(c_id),
    FOREIGN KEY (seller_id) REFERENCES Sellers(seller_id)
);

CREATE TABLE Wishlist (
    wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

CREATE TABLE Reviews (
    r_id INT PRIMARY KEY AUTO_INCREMENT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    product_id INT,
    r_date DATE DEFAULT CURRENT_DATE,
    reviewer INT,
    comment TEXT,
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (reviewer) REFERENCES Users(user_id)
);

CREATE TABLE ShoppingCartItems (
    position INT,
    cart_id INT,
    product_id INT,
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (position, cart_id),
    FOREIGN KEY (cart_id) REFERENCES ShoppingCarts(cart_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    delivery_address VARCHAR(255) NOT NULL,
    payment_id INT,
    shopping_cart_id INT,
    user_id INT,
    status VARCHAR(255) NOT NULL,
    FOREIGN KEY (shopping_cart_id) REFERENCES ShoppingCarts(cart_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE PaymentMethods (
    pm_id INT PRIMARY KEY AUTO_INCREMENT,
    pm_name VARCHAR(100) NOT NULL
);

CREATE TABLE Payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    method_id INT,
    p_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (method_id) REFERENCES PaymentMethods(pm_id)
);

CREATE TABLE Subscriptions (
    sub_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    seller_id INT,
    sub_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (seller_id) REFERENCES Sellers(seller_id)
);

CREATE TABLE Messaging (
    m_id INT PRIMARY KEY AUTO_INCREMENT,
    sending_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    sender_id INT,
    receiver_id INT,
    FOREIGN KEY (sender_id) REFERENCES Users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES Users(user_id)
);

-- Erstellen des Views für Produktinformationen
CREATE VIEW IF NOT EXISTS ProductInfo AS
SELECT 
    p.product_id AS ProductID,
    p.name AS ProductName,
    p.cost AS Cost,
    p.available_copies AS AvailableCopies,
    c.name AS CategoryName,
    s.shopname AS SellerName
FROM Products p
JOIN Category c ON p.category_id = c.c_id
JOIN Sellers s ON p.seller_id = s.seller_id;

-- Erstellen des Views für Nachrichten zwischen Nutzern
CREATE VIEW IF NOT EXISTS UserMessages AS
SELECT 
    m.m_id AS MessageID,
    m.sending_date AS SendingDate,
    m.message AS MessageContent,
    s.username AS SenderUsername,
    r.username AS ReceiverUsername
FROM Messaging m
JOIN Users s ON m.sender_id = s.user_id
JOIN Users r ON m.receiver_id = r.user_id;

-- korrelierte subquery
SELECT c.name
FROM Category c
WHERE NOT EXISTS (
    SELECT 1
    FROM Products p
    WHERE p.category_id = c.c_id
    AND p.available_copies > 0
);

-- unkorrelierte subquery
SELECT name, cost
FROM Products
WHERE cost > (
    SELECT AVG(cost)
    FROM Products
);


-- Index für die `category_id`-Spalte in der `Products`-Tabelle
CREATE INDEX idx_category_id ON Products (category_id);

-- Index für die `email`-Spalte in der `Users`-Tabelle
CREATE INDEX idx_email ON Users (email);


