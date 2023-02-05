### Hexlet tests and linter status:
[![Actions Status](https://github.com/Zlober/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Zlober/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/68276b7a11956a1fd0ed/maintainability)](https://codeclimate.com/github/Zlober/python-project-83/maintainability)

https://python-project-83-production-f0c1.up.railway.app/

Page Analyzer is a full-featured application based on the Flask framework that analyzes specified pages for SEO suitability.

Here the basic principles of building modern websites on the MVC architecture are used: working with routing, query handlers and templating, interaction with the database.

In this project the Bootstrap 5 framework along with Jinja2 template engine are used. The frontend is rendered on the backend. This means that the page is built by the Jinja2 backend, which returns prepared HTML. And this HTML is rendered by the server.

PostgreSQL is used as the object-relational database system with Psycopg library to work with PostgreSQL directly from Python.

### Installation
To use the application, you need to clone the repository to your computer. This is done using the git clone command. Clone the project:
>> git clone https://github.com/ivnvxd/python-project-83.git && cd python-project-83

Then you have to install all necessary dependencies:
>> make install 

Create .env file in the root folder and add following variables:
>> DATABASE_URL = postgresql://{provider}://{user}:{password}@{host}:{port}/{db}
> 
>> SECRET_KEY = '{your secret key}'

Run commands from database.sql to create the required tables.

### Usage
Start the gunicorn Flask server by running:
>> make start

To add a new site, enter its address into the form on the home page. The specified address will be validated and then added to the database.

After the site is added, you can start checking it. A button appears on the page of a particular site, and clicking on it creates an entry in the validation table.

You can see all added URLs on the /urls page.