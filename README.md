# Bookstore Platform

A web-based bookstore platform built with Flask and PostgreSQL, featuring role-based access control, parallel processing capabilities, and inventory management.

## Features

- **User Roles & Authentication**

  - Customer: Browse products, manage cart, place orders
  - Vendor: List products, manage inventory, track sales 
  - Employee: Process orders, update inventory, customer service
  - Admin: Full system access and configuration

- **Core Functionality**
  - Product catalog with search and filtering
  - Shopping cart and secure checkout
  - Order tracking and management
  - Inventory management

## Tech Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login, Flask-Security


### How to create and connect you to own database
so as of right now, we are going to stick to using and running our own databases on your local machines. Sharanya is currently working with the IT department for us to work with Azure which will help us move from our local machines to a shared and accessible platform which will need to happen anyways according to sharanya so the quicker the better. 

read this to help: https://neon.com/postgresql/postgresql-python/connect 

^i had to manipulate my path enviroment settings to allow the psql - U postgres to run since it was in a completely different directory. 

Go in and follow the steps, when we get to create a new database, run the command CREATE DATABASE dejiji_db;
you should get a confirmation message to know it was created sucessfully

you can login to PGAdmin and the new db name should pop up

create an .env file for your personal use
DB_NAME='dejiji_db'
DB_USER='xxx'
DB_PASS='xxx'
the xxx comes from when you set up PGAdmin and will vary between everyone for now until we get access to Azure

###HTML pages to add### 
-Customer: home, login, sign up, about us, checkout (need cart), search, customer service
-Vendor: insert/delete/traking sales of books
-Employee/Owner: customer service (insert transacion id to look up/ query by name), access to everything else (no vendor)
