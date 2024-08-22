
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

CREATE TABLE Visitors (
    v_id INT PRIMARY KEY AUTO_INCREMENT,
    ip VARCHAR(45) NOT NULL
);

CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    acc_creation_date DATE DEFAULT CURRENT_DATE,
    cart_id INT,
    email VARCHAR(255) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Visitors(v_id) ON DELETE CASCADE
);

CREATE TABLE Sellers (
    seller_id INT PRIMARY KEY,
    shopname VARCHAR(255) NOT NULL,
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
    source VARCHAR(255) NOT NULL
    
);

CREATE TABLE Category (
    c_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    superiorc_id INT,
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
