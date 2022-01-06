# Store

Django 3 online store repository

## Installation

1. Download project from github;
2. Go to directory `store` in cmd;
3. For creating database run following commands: 
   - `python manage.py makemigrations` 
   - `python manage.py migrate`
4. To create an admin - `python manage.py createsuperuser`;
5. Run server - `python manage.py runserver`;
6. In your browser go to "http://127.0.0.1:8000" (this is the main page of site)

## Site management

- At "http://127.0.0.1:8000/admin" located the admin page
- For creating a customer of user go to "Customers" on the left side of the screen
- For creating a category for products go to "Categories"
- For creating a product go to "Products" 
- For manage users rights you can go to "Users" and "Groups"
- For add characteristics to a specific category of products follow this link "http://127.0.0.1:8000/product-specs/"

## Usage

- On the main page of the site you can see all products that exist
- On the navbar, you can choose a specific category of products (also you can filter products on the page of a specific category)
- You can also login or sing-up from the main page
- You can add products in your cart, there you can change quantity, delete some products and make orders
- If you go to your profile page, you will be able to view all the details of your latest orders
