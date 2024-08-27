

-- Füge Benutzer hinzu
INSERT INTO Users (user_id, username, password, email) VALUES 
(1, 'john_doe', 'hashed_password_1', 'john@example.com'),
(2, 'jane_smith', 'hashed_password_2', 'jane@example.com'),
(3, 'fülle', 'hashed_password_2', 'fülle@example.com');

-- Füge einige ShoppingCarts hinzu
INSERT INTO ShoppingCarts (user_id, created_at) VALUES 
(1, NOW()),
(2, NOW());

-- Füge Verkäufer hinzu
INSERT INTO Sellers (seller_id, shopname, rating) VALUES 
(1, 'John\'s Store', 4.5),
(2, 'Jane\'s Boutique', 3.8);

-- Füge einige Bilder hinzu
INSERT INTO Pictures (source) VALUES 
('images/Smartphone.jpg'),
('images/Kopfhörer.jpg');

-- Füge Kategorien hinzu
INSERT INTO Category (name, description, superiorc_id) VALUES 
('Electronics', 'Devices and gadgets', NULL),
('Books', 'Various kinds of books', 1);

-- Füge Produkte hinzu
INSERT INTO Products (picture_id, cost, available_copies, category_id, information, seller_id, name) VALUES 
(1, 199.99, 10, 1, 'Latest model of smartphone.', 1, 'Smartphone'),
(2, 30.99, 50, 2, 'Bluetooth Kopfhörer.', 2, 'Kopfhörer');

-- Füge Bewertungen hinzu
INSERT INTO Reviews (rating, product_id, reviewer, comment) VALUES 
(5, 1, 1, 'Amazing smartphone!'),
(4, 2, 2, 'Very informative book.');

-- Füge Einkaufswagenartikel hinzu
INSERT INTO ShoppingCartItems (position, cart_id, product_id, quantity) VALUES 
(1, 1, 1, 1),
(2, 2, 2, 2);

-- Füge Bestellungen hinzu
INSERT INTO Orders (delivery_address, user_id, status, shopping_cart_id) VALUES 
('123 Main St', 1,'completed', 1),
('456 Elm St', 2, 'Pending', 2);

-- Füge Zahlungsmethoden hinzu
INSERT INTO PaymentMethods (pm_name) VALUES 
('Credit Card'),
('PayPal');

-- Füge Zahlungen hinzu
INSERT INTO Payments (order_id, method_id) VALUES 
(1, 1),
(2, 2);

-- Füge Abonnements hinzu
INSERT INTO Subscriptions (user_id, seller_id) VALUES 
(1, 1),
(2, 2);

-- Füge Nachrichten hinzu
INSERT INTO Messaging (message, sender_id, receiver_id) VALUES 
('Hello, how are you?', 1, 2),
("I\'m good, thank you!", 2, 1);




