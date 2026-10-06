-- Movie Ticket Management System: database structure (no user data)
-- Run this once in MySQL Workbench, then create your own .env file.

CREATE DATABASE IF NOT EXISTS movie_ticket_booking;
USE movie_ticket_booking;

CREATE TABLE IF NOT EXISTS theaters (
    theater_id INT AUTO_INCREMENT PRIMARY KEY,
    theater_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    theater_id INT NOT NULL,
    seat_number VARCHAR(5) NOT NULL,
    seat_type VARCHAR(20) NOT NULL,
    seat_price DECIMAL(10,2) NOT NULL,
    is_blocked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (theater_id) REFERENCES theaters(theater_id),
    UNIQUE (theater_id, seat_number)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    mobile VARCHAR(10) UNIQUE NOT NULL,
    username VARCHAR(30) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_name VARCHAR(100) NOT NULL,
    genre VARCHAR(30) NOT NULL,
    language VARCHAR(30) NOT NULL,
    duration INT NOT NULL,
    release_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS shows (
    show_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    theater_id INT NOT NULL,
    show_date DATE NOT NULL,
    show_time TIME NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (theater_id) REFERENCES theaters(theater_id)
);

-- No UNIQUE(show_id, seat_id) here on purpose: cancelled bookings stay in the
-- table (status = 'Cancelled'), and that seat must be bookable again.
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    show_id INT NOT NULL,
    seat_id INT NOT NULL,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Booked',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (show_id) REFERENCES shows(show_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id),
    INDEX idx_bookings_show_seat (show_id, seat_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT UNIQUE NOT NULL,
    payment_mode VARCHAR(20) NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_date DATETIME NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

CREATE TABLE IF NOT EXISTS admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_username VARCHAR(50) NOT NULL UNIQUE,
    admin_password VARCHAR(255) NOT NULL,
    admin_email VARCHAR(100) NOT NULL UNIQUE
);

-- Starting admin login. CHANGE the password and email after your first login.
INSERT INTO admins (admin_username, admin_password, admin_email)
VALUES ('admin123', 'admin123', 'your_email@gmail.com');