# Store API  

Live Demo: [Demo Link](https://a195.pythonanywhere.com/instructions/) 

This is a backend API for managing a store, built with Django and Django REST Framework. It provides a robust solution for handling store operations with optimised database queries, secure authentication, and a clean API structure.  

---

## **API Root**  

The API includes the following models:  

- **Comment:** Represents product comments.  
- **Category:** Represents product categories.  
- **Discount:** Represents product discounts.  
- **Product:** Represents store products.  
- **Customer:** Represents customers registered in the system.  
- **OrderItem, Order:** Represents customer orders with nested items.  
- **CartItem, Cart:** Allows anonymous cart creation using UUIDs.  

---

## **Key Features**  

- **Admin and Test User Accounts for Testing:**  
  - Admin: `admin` / `password`  
  - Test User: `user` / `password`  

- **Admin Panel Access:**  
  - Explore the admin panel to manage products, categories, and orders.  
  - [Go to Admin Panel](https://a195.pythonanywhere.com/admin/)  

- **Secure Authentication:**  
  - Authentication is handled via Djoser and JWT.  
  - **Token Expiry Details:**  
    - Refresh Token: Expires in 1 day.  
    - Access Token: Expires in 30 minutes.  

- **Database Optimisation:**  
  - Django Debug Toolbar is integrated for query analysis and optimisation.  
  - Fake data is generated using `Faker` and `Factory Boy`.  

---

## **Authentication Guide**  

To access the API, follow these steps:  

### **1. Log In**  
Use the provided credentials to log in and generate tokens:  
- **Admin:** `admin` / `password`  
- **Test User:** `user` / `password`  

[Create Token](https://a195.pythonanywhere.com/auth/jwt/create/)  

### **2. Refresh Access Token**  
When your access token expires (in 30 minutes), refresh it by making a POST request to the following endpoint:  

[Refresh Token](https://a195.pythonanywhere.com/auth/jwt/refresh/)  

You will receive a new access token in return.  

### **3. Add Tokens to Requests**  
Use the generated tokens to authenticate requests:  

- **ModHeader (Chrome Extension):** Add the following header:  
- Authorization JWT {access toke}

- **Postman:**  
- Go to the "Authorization" tab.  
- Select "Bearer Token" as the type.  
- Paste the access token in the token field.  

### **4. Explore the Browsable API**  
Once authenticated, you can explore the API.  

- **Admin Users:** Manage products, categories, and orders.  
- **Test Users:** View products, create carts, and place orders.  

---

## **How to Use the API**  

### **Create a UUID for a Cart**  
1. Create a cart by sending a POST request to `/store/carts/`.  
2. Copy the generated cart ID and use it to add items to the cart by sending a POST request to `/store/carts/{UUID}/items`. 
3. Submit the cart to place an order by sending a POST request with the cart ID to`/store/orders/`. The cart will be deleted after the order is placed.  

---

## **Quick Start**  

1. **Set up the Python Virtual Environment**  
   ```bash  
   python3 -m venv venv  
   source venv/bin/activate  # For Linux/MacOS  
   venv\Scripts\activate     # For Windows  

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt  

3. **Set up the Database**
    ```bash
    python manage.py makemigrations  
    python manage.py migrate  

4. **Collect Static Files**
    ```bash
    python manage.py collectstatic  

5. **Create a Superuser**
    ```bash
    python manage.py createsuperuser  

6.**Populate the Database with Fake Data**
    ```bash
    python manage.py setup_fake_data  

7.**Run the Development Server**
    ```bash
    python manage.py runserver  



### Deployment Information  
The application is hosted on **PythonAnywhere**.  

### Technologies Used
- **Backend:** Django, Django REST Framework
- **Authentication:** Djoser, JWT
- **Database:** SQLite (default)
- **Testing and Mock Data:** Factory Boy, Faker
- **Development Tools:** Django Debug Toolbar