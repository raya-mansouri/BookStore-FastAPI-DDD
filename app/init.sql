INSERT INTO city (name) VALUES 
('New York'), ('Los Angeles'), ('Chicago'), ('Houston'), ('Phoenix'),
('San Diego'), ('Dallas'), ('San Francisco'), ('Miami'), ('Seattle')
ON CONFLICT DO NOTHING;

INSERT INTO genre (name) VALUES 
('Science Fiction'), ('Fantasy'), ('Mystery'), ('Thriller'), ('Romance'),
('Historical'), ('Non-fiction'), ('Biography'), ('Horror'), ('Self-Help')
ON CONFLICT DO NOTHING;

INSERT INTO "user" (username, first_name, last_name, phone, email, password, role, is_active) VALUES 
('admin1', 'Alice', 'Smith', '12345678901', 'alice@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'admin', TRUE),
('cust1', 'John', 'Doe', '98765432101', 'john@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'customer', TRUE),
('cust2', 'Emma', 'Johnson', '19283746501', 'emma@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'customer', TRUE),
('cust3', 'Liam', 'Brown', '56473829101', 'liam@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'customer', TRUE),
('cust4', 'Sophia', 'Wilson', '10293847501', 'sophia@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'customer', TRUE),
('cust5', 'James', 'Taylor', '12309876501', 'james@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'customer', TRUE),
('author1', 'Michael', 'Anderson', '23456789012', 'michael@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'author', TRUE),
('author2', 'Sarah', 'Martinez', '34567890123', 'sarah@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'author', TRUE),
('author3', 'David', 'Hernandez', '45678901234', 'david@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'author', TRUE),
('author4', 'Emily', 'Garcia', '56789012345', 'emily@example.com', '$2b$12$8IyEYrOWyenh2a50zChbKefl/YFcOjolclawdYw.I5EEGRHFIsSsa', 'author', TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO author (user_id, city_id, goodreads_link, bank_account_number) VALUES
(7, 1, 'https://goodreads.com/michael', '1111222233334444'),
(8, 2, 'https://goodreads.com/sarah', '2222333344445555'),
(9, 3, 'https://goodreads.com/david', '3333444455556666'),
(10, 4, 'https://goodreads.com/emily', '4444555566667777')
ON CONFLICT DO NOTHING;

INSERT INTO customer (user_id, subscription_model, subscription_end_time, wallet_money_amount) VALUES
(2, 'plus', NOW() + INTERVAL '10 days', 500000),
(3, 'free', NOW() + INTERVAL '1 month', 0),
(4, 'premium', NOW() + INTERVAL '11 days', 2000),
(5, 'plus', NOW() + INTERVAL '6 days', 75000),
(6, 'free', NOW() + INTERVAL '3 days', 150000)
ON CONFLICT DO NOTHING;

INSERT INTO book (title, isbn, price, genre_id, description, units, reserved_units) VALUES
('Dune', '9780441013593', 15000, 1, 'A sci-fi classic.', 10, 2),
('Harry Potter', '9780747532743', 12000, 2, 'A fantasy adventure.', 15, 3),
('Sherlock Holmes', '9780451524935', 1300, 3, 'A detective novel.', 12, 1),
('Gone Girl', '9780307588371', 1400, 4, 'A psychological thriller.', 8, 2),
('Pride and Prejudice', '9780141439518', 110000, 5, 'A romantic novel.', 9, 0)
ON CONFLICT DO NOTHING;

-- Insert authors into book_author_table (adjust IDs as needed)
-- For example, for 'Dune' which has authors with ids 1 and 2:
INSERT INTO book_author (book_id, author_id) VALUES
(1, 1), -- Dune with Author(id=1)
(1, 2), -- Dune with Author(id=2)
(2, 3), -- Harry Potter with Author(id=3)
(3, 4), -- Sherlock Holmes with Author(id=4)
(4, 1), -- Gone Girl with Author(id=1)
(4, 3), -- Gone Girl with Author(id=3)
(5, 4), -- Pride and Prejudice with Author(id=4)
(5, 2); -- Pride and Prejudice with Author(id=2)


INSERT INTO reservation (customer_id, book_id, start_of_reservation, end_of_reservation, price, status, queue_position) VALUES
(1, 1, NOW(), NOW() + INTERVAL '7 days', 150000, 'pending', NULL),
(2, 2, NOW(), NOW() + INTERVAL '5 days', 120000, 'active', NULL),
(3, 3, NOW(), NOW() + INTERVAL '10 days', 130000, 'completed', NULL),
(4, 4, NOW(), NOW() + INTERVAL '3 days', 140000, 'pending', NULL),
(5, 5, NOW(), NOW() + INTERVAL '1 month', 110000, 'active', NULL)
ON CONFLICT DO NOTHING;
