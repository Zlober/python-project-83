DROP DATABASE IF EXISTS pages;

CREATE DATABASE pages;
    CREATE TABLE urls (
        id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name varchar(255),
        created_at date
    );
    CREATE TABLE url_checks (
        id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        url_id bigint REFERENCES urls(id),
        status_code int,
        h1 varchar(255),
        title varchar(255),
        description text,
        created_at date
    );