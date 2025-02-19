CREATE TYPE user_roles AS ENUM ('admin', 'customer', 'author');
CREATE TYPE subscription_models AS ENUM ('free', 'plus', 'premium');
CREATE TYPE reservation_status AS ENUM ('pending', 'active', 'completed');

CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(11) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role user_roles NOT NULL,
    is_active BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE IF NOT EXISTS city (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS genre (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS author (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES "user"(id),
    city_id INTEGER NOT NULL REFERENCES city(id),
    goodreads_link VARCHAR(255),
    bank_account_number VARCHAR(16) NOT NULL
);

CREATE TABLE IF NOT EXISTS customer (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES "user"(id),
    subscription_model subscription_models NOT NULL,
    subscription_end_time TIMESTAMP DEFAULT NOW(),
    wallet_money_amount INTEGER DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS book (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    price INTEGER DEFAULT 0 NOT NULL,
    genre_id INTEGER NOT NULL REFERENCES genre(id),
    description VARCHAR(1000),
    units INTEGER NOT NULL,
    reserved_units INTEGER DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS reservation (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(id),
    book_id INTEGER NOT NULL REFERENCES book(id),
    start_of_reservation TIMESTAMP DEFAULT NOW() NOT NULL,
    end_of_reservation TIMESTAMP DEFAULT NOW() NOT NULL,
    price INTEGER NOT NULL,
    status reservation_status DEFAULT 'pending',
    queue_position INTEGER
);

CREATE TABLE IF NOT EXISTS book_author (
    book_id INTEGER NOT NULL REFERENCES book(id),
    author_id INTEGER NOT NULL REFERENCES author(id),
    PRIMARY KEY (book_id, author_id)
);

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

INSERT INTO reservation (customer_id, book_id, start_of_reservation, end_of_reservation, price, status, queue_position) VALUES
(1, 1, NOW(), NOW() + INTERVAL '7 days', 150000, 'pending', NULL),
(2, 2, NOW(), NOW() + INTERVAL '5 days', 120000, 'active', NULL),
(3, 3, NOW(), NOW() + INTERVAL '10 days', 130000, 'completed', NULL),
(4, 4, NOW(), NOW() + INTERVAL '3 days', 140000, 'pending', NULL),
(5, 5, NOW(), NOW() + INTERVAL '1 month', 110000, 'active', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO book_author (book_id, author_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 2)
ON CONFLICT DO NOTHING;

