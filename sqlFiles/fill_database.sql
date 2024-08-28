INSERT INTO Users (username, password, email) VALUES
('alice', 'password123', 'alice@example.com'),
('bob', 'securepass', 'bob@example.com'),
('carol', 'mypassword', 'carol@example.com');

INSERT INTO Sellers (seller_id  , shopname, website_url, rating) VALUES
(1, 'Tech Haven', 'http://techhaven.com', 4.5),
(2, 'Book Nook', 'http://booknook.com', 4.2),
(3, 'Gourmet Goods', 'http://gourmetgoods.com', 4.8);

INSERT INTO ShoppingCarts (user_id) VALUES
(1),
(2),
(3);

INSERT INTO Pictures (source) VALUES
('https://cdn.idealo.com/folder/Product/203235/7/203235721/s1_produktbild_gross/apple-iphone-15.jpg'),
('https://rukminim1.flixcart.com/image/300/300/l51d30w0/book/c/z/q/c-programming-language-comprehensive-book-2022-original-imagfsqwmhyepk7n.jpeg'),
('https://oliveoillovers.com/cdn/shop/products/crete-gourmet-5L.jpg?v=1648218839');

INSERT INTO Category (name, description, superiorc_id) VALUES
('Electronics', 'Devices and gadgets', NULL),
('Smartphones', 'Handy', 1),
('Books', 'All kinds of books', NULL),
('Food', 'Gourmet and everyday food items', NULL);

INSERT INTO Products (picture_id, cost, available_copies, category_id, seller_id, name, information) VALUES
(1, 299.99, 10, 2, 1, 'Smartphone XYZ', 'Latest model with high performance'),
(2, 19.99, 100, 3, 2, 'Programming 101', 'A beginner\'s guide to programming'),
(3, 5.99, 50, 4, 3, 'Gourmet Olive Oil', 'High quality olive oil from Italy');

INSERT INTO Reviews (rating, product_id, reviewer, comment) VALUES
(5, 1, 1, 'Excellent smartphone, highly recommend!'),
(4, 2, 2, 'Great book for beginners, but a bit basic.'),
(5, 3, 3, 'Best olive oil I have ever tasted!');

INSERT INTO ShoppingCartItems (position, cart_id, product_id, quantity) VALUES
(1, 1, 1, 1),
(2, 2, 2, 3),
(1, 3, 3, 2);

INSERT INTO Orders (delivery_address, shopping_cart_id, user_id, status) VALUES
('123 Elm Street', 1, 1, 'Shipped'),
('456 Maple Avenue', 2, 2, 'Processing'),
('789 Oak Drive', 3, 3, 'Delivered');

INSERT INTO PaymentMethods (pm_name) VALUES
('Credit Card'),
('PayPal'),
('Bank Transfer');

INSERT INTO Payments (order_id, method_id, p_date) VALUES
(1, 1, '2024-08-28'),
(2, 2, '2024-08-28'),
(3, 3, '2024-08-28');

INSERT INTO Subscriptions (user_id, seller_id) VALUES
(1, 1),
(2, 2),
(3, 3);

INSERT INTO Messaging (message, sender_id, receiver_id) VALUES
('Hello, I have a question about your product.', 1, 2),
('Thanks for your purchase!', 2, 1),
('Can you provide more details on the delivery?', 3, 1);

 