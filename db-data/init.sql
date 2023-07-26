CREATE DATABASE peppol_builder;
USE peppol_builder;

CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

INSERT INTO users (name, email, password) VALUES
  ('Alice', 'alice@example.com', 'password1'),
  ('Bob', 'bob@example.com', 'password2'),
  ('Charlie', 'charlie@example.com', 'password3');