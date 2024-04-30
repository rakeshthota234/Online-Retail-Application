import streamlit as st
import sqlite3
import pandas as pd
import ast
from datetime import datetime
import random


# Connect to the SQLite database
conn = sqlite3.connect('online_retail123.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS item_categories
             (item_category varchar(40) PRIMARY KEY)''')

c.execute('''CREATE TABLE IF NOT EXISTS items
             (item_id INTEGER ,
              item_name varchar(40) NOT NULL,
              item_category varchar(40),
              mfg_date date,
              exp_date date,
              item_price decimal(10, 2) DEFAULT 0.00,
              FOREIGN KEY(item_category) REFERENCES item_categories(item_category)
              ON DELETE RESTRICT ON UPDATE CASCADE,
              CHECK (item_price >= 0.00))''')

c.execute('''CREATE TABLE IF NOT EXISTS customer 
             (email varchar(100) PRIMARY KEY,
              password varchar(100) NOT NULL,
              first_name varchar(20) NOT NULL,
              last_name varchar(20),
              age smallint,
              sex char(1),
              phone_number char(10) NOT NULL,
              CHECK (age > 0))''')

c.execute('''CREATE TABLE IF NOT EXISTS zipcode
             (zip int PRIMARY KEY,
              city varchar(40),
              state varchar(40),
              county varchar(40))''')

c.execute('''CREATE TABLE IF NOT EXISTS address
             (address_id int,
              email varchar(100),
              zip int,
              full_address text,
             
              FOREIGN KEY(zip) REFERENCES zipcode(zip)
              ON DELETE RESTRICT ON UPDATE CASCADE,
              FOREIGN KEY(email) REFERENCES customer(email)
              ON DELETE CASCADE ON UPDATE CASCADE)''')

c.execute('''CREATE TABLE IF NOT EXISTS payment
             (payment_id int,
              email varchar(100),
              is_payment_cash boolean NOT NULL,
              credit_card_number char(16) NOT NULL,
              FOREIGN KEY(email) REFERENCES customer(email)
              ON DELETE CASCADE ON UPDATE CASCADE)''')

c.execute('''CREATE TABLE IF NOT EXISTS order_status
             (status varchar(30) PRIMARY KEY)''')

c.execute('''CREATE TABLE IF NOT EXISTS payment_status
             (status varchar(30) PRIMARY KEY)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders
             (order_id int PRIMARY KEY,
              email varchar(100),
              address_id int,
              total_amount decimal(10, 2),
              date_of_order date,
              date_of_service date,
              status_of_order varchar(30),
              FOREIGN KEY(email, address_id) REFERENCES address(email, address_id),
              FOREIGN KEY(status_of_order) REFERENCES order_status(status))''')

c.execute('''CREATE TABLE IF NOT EXISTS order_item
             (item_id int,
              order_id int,
              email varchar(100),
              price decimal(10, 2),
              PRIMARY KEY(item_id, order_id),
              FOREIGN KEY(item_id) REFERENCES items(item_id),
              FOREIGN KEY(email, order_id) REFERENCES orders(email, order_id))''')

c.execute('''CREATE TABLE IF NOT EXISTS voucher
             (voucher_id char(5) PRIMARY KEY,
              discount_price decimal(10, 2))''')

c.execute('''CREATE TABLE IF NOT EXISTS billing
             (billing_id int,
              order_id int,
              payment_id int,
              email varchar(100),
              voucher_id char(5),
              final_amount decimal(10, 2),
              status_of_payment varchar(30),
              FOREIGN KEY(email, order_id) REFERENCES orders(email, order_id),
              FOREIGN KEY(email, payment_id) REFERENCES payment(email, payment_id),
              FOREIGN KEY(voucher_id) REFERENCES voucher(voucher_id),
              FOREIGN KEY(status_of_payment) REFERENCES payment_status(status))''')

@st.cache_data
def load_item_data():
    item_data = pd.read_csv('address.csv').head(100)
    item_data.to_sql('address', conn, if_exists='append', index=False)
    item_data = pd.read_csv('items.csv').head(100)
    item_data.to_sql('items', conn, if_exists='append', index=False)
    item_data = pd.read_csv('billing.csv').head(100)
    item_data.to_sql('billing', conn, if_exists='append', index=False)
    item_data = pd.read_csv('customer.csv').head(100)
    item_data.to_sql('customer', conn, if_exists='append', index=False)
    item_data = pd.read_csv('item_categories.csv').head(100)
    item_data.to_sql('item_categories', conn, if_exists='append', index=False)
    item_data = pd.read_csv('order_item.csv').head(100)
    item_data.to_sql('order_item', conn, if_exists='append', index=False)
    item_data = pd.read_csv('orders.csv').head(100)
    item_data.to_sql('orders', conn, if_exists='append', index=False)
    item_data = pd.read_csv('payment.csv').head(100)
    item_data.to_sql('payment', conn, if_exists='append', index=False)
    item_data = pd.read_csv('uszipcodes.csv').head(100)
    item_data.to_sql('uszipcodes', conn, if_exists='append', index=False)
    item_data = pd.read_csv('voucher.csv').head(100)
    item_data.to_sql('voucher', conn, if_exists='append', index=False)

# Function to fetch items from the database
@st.cache_data
def fetch_items():
    c.execute("SELECT * FROM items LIMIT 10")
    return c.fetchall()

@st.cache_data
def fetch_item_by_id(item_id):
    c.execute("SELECT * FROM items WHERE item_id=?", (item_id,))
    return c.fetchone()

@st.cache_data
def fetch_categories():
    c.execute("SELECT DISTINCT item_category FROM items")
    return [row[0] for row in c.fetchall()]

# Function to fetch items by category from the database
@st.cache_data
def fetch_items_by_category(category):
    c.execute("SELECT * FROM items WHERE item_category=?", (category,))
    return c.fetchall()

def generate_unique_order_id():
    while True:
        order_id = random.randint(100000, 999999)
        c.execute("SELECT COUNT(*) FROM orders WHERE order_id=?", (order_id,))
        if c.fetchone()[0] == 0:  # If the order_id is not present in the database
            print("jdjhd", order_id)
            return order_id
        
def generate_unique_payment_id():
   
    while True:
        order_id = random.randint(100000, 999999)
        c.execute("SELECT COUNT(*) FROM payment WHERE payment_id=?", (order_id,))
        if c.fetchone()[0] == 0:  # If the order_id is not present in the database
            print("jdjhd", order_id)
            return order_id



def add_order(email, address_id, total_amount, date_of_order, date_of_service, status_of_order):
    # Retrieve email from the address table
    order_id = generate_unique_order_id()
    st.session_state.order_details = (email, order_id)
    # Insert order details into the orders table
    c.execute("INSERT INTO orders (order_id, email, address_id, total_amount, date_of_order, date_of_service, status_of_order) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (order_id, email, address_id, total_amount, date_of_order, date_of_service, status_of_order))
    conn.commit()

    st.success("Order added successfully!")


    
def add_data():
    st.subheader("Add Customer Details")

    # Customer details
    st.subheader("Customer Details")
    email = st.text_input("Email")

    password = st.text_input("Password", type="password")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    age = st.number_input("Age", min_value=1, max_value=150)
    sex = st.radio("Sex", options=["M", "F"])
    phone_number = st.text_input("Phone Number")

    # Address details
    st.subheader("Address Details")
    address_id = st.number_input("Address ID")
    zip_code = st.text_input("Zip Code")
    full_address = st.text_area("Full Address")

    # Zip code details
    st.subheader("Zip Code Details")
    city = st.text_input("City")
    state = st.text_input("State")
    county = st.text_input("County")

    if st.button("Add Data"):
        # Insert data into customer table
        c.execute("INSERT INTO customer VALUES (:email, :password, :first_name, :last_name, :age, :sex, :phone_number)",
                  {'email': email, 'password': password, 'first_name': first_name, 'last_name': last_name,
                   'age': age, 'sex': sex, 'phone_number': phone_number})
        conn.commit()

        # Insert data into address table
        c.execute("INSERT INTO address VALUES (:address_id, :email, :zip, :full_address)",
                  {'address_id': address_id, 'email': email, 'zip': zip_code, 'full_address': full_address})
        conn.commit()

        # Insert data into zip code table
        c.execute("INSERT INTO zipcode VALUES (:zip, :city, :state, :county)",
                  {'zip': zip_code, 'city': city, 'state': state, 'county': county})
        conn.commit()

        # st.success("Data added successfully!")
        # order_id = generate_unique_order_id()

        # Get current date and time
        date_of_order = datetime.now().date()
        date_of_service = datetime.now().date()  # Update as needed
        status_of_order = "Successful"  # Update as needed
        
        # Add order to the orders table
        add_order(email, address_id, total_amount=10.99, date_of_order=date_of_order, date_of_service=date_of_service, status_of_order=status_of_order)
        # return email
        


# @st.cache_data
def view_data():
    st.subheader("View Data")
    table = st.selectbox("Select table to view", ("Customer","Address","Items","order_item","orders","item_categories", "billing","payment", "zipcode"))
    if table == "Customer":
            items_df = pd.read_sql('SELECT * FROM customer', conn)
            st.write(items_df)

    elif table == "Address":
            items_df = pd.read_sql('SELECT * FROM address', conn)
            st.write(items_df)
    elif table == "Items":
            items_df = pd.read_sql('SELECT * FROM items', conn)
            st.write(items_df)

    elif table == "order_item":
            items_df = pd.read_sql('SELECT * FROM order_item', conn)
            st.write(items_df)
    elif table == "orders":
            items_df = pd.read_sql('SELECT * FROM orders', conn)
            st.write(items_df)
    elif table == "item_categories":
            items_df = pd.read_sql('SELECT * FROM item_categories', conn)
            st.write(items_df)
    
    elif table == "billing":
            items_df = pd.read_sql('SELECT * FROM billing', conn)
            st.write(items_df)
    elif table == "payment":
            orders_df = pd.read_sql('SELECT * FROM payment', conn)
            st.write(orders_df)
    elif table == "zipcode":
            customer_df = pd.read_sql('SELECT * FROM zipcode', conn)
            
            st.write(customer_df)
    
    
def add_payment(email, is_payment_cash, credit_card_number, payment_id):
    # Generate a unique payment ID
    
    # Insert payment details into the payments table
    c.execute("INSERT INTO payment (payment_id, email, is_payment_cash, credit_card_number) VALUES (?, ?, ?, ?)",
              (payment_id, email, is_payment_cash, credit_card_number))
    conn.commit()

    

def payment_page():
    st.title('Payment')
   
    # Retrieve order details from session state
    email, address_id = st.session_state.order_details

    # Display payment form
    st.subheader("Payment Details")
    is_payment_cash = st.checkbox("Payment by Cash")
    
    if is_payment_cash:
        # st.write("Payment by cash selected. No credit card number required.")
        credit_card_number = st.text_input("Credit Card Number")  # Set credit card number to None if payment by cash
    else:
        credit_card_number = st.text_input("Credit Card Number")

    # Display email (retrieved from order details)
    st.write(f"Email: {email}")

    # Generate unique payment ID
    payment_id = generate_unique_payment_id()

    # Display payment ID
    st.write(f"Payment ID: {payment_id}")

    if st.button("Confirm Payment"):
        # Add payment details to the database
        add_payment(email, is_payment_cash, credit_card_number, payment_id)
        st.success("Payment was successful!")

def generate_unique_billing_id():
    # Generate a unique billing ID
    while True:
        billing_id = random.randint(1000, 9999)  # Adjust range as needed
        c.execute("SELECT COUNT(*) FROM billing WHERE billing_id=?", (billing_id,))
        if c.fetchone()[0] == 0:  # If the billing_id is not present in the database
            return billing_id

def fetch_order_details(email):
    # Fetch order details based on the email
    c.execute("SELECT * FROM orders WHERE email=?", (email,))
    return c.fetchone()  # Assuming only one order per email for simplicity

def add_billing(order_id, payment_id, email, voucher_id, final_amount, status_of_payment):
    # Insert billing details into the billing table
    billing_id = generate_unique_billing_id()
    c.execute("INSERT INTO billing (billing_id, order_id, payment_id, email, voucher_id, final_amount, status_of_payment) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (billing_id, order_id, payment_id, email, voucher_id, final_amount, status_of_payment))
    conn.commit()
def fetch_payment_details(email):
    # Fetch payment details based on the email
    c.execute("SELECT * FROM payment WHERE email=?", (email,))
    return c.fetchone()  # Assuming only one payment per email for simplicity


def billing_page():
    st.title('Billing')
   
    # Retrieve order and payment details
    email, _ = st.session_state.order_details
    order_details = fetch_order_details(email)
    payment_details = fetch_payment_details(email)

    # Set default values
    voucher_id = "No voucher applied"
    final_amount = 10.99  # Assuming fixed amount for now
    status_of_payment = "Successful"

    if order_details and payment_details:
        order_id = order_details[0]
        payment_id = payment_details[0]

        # Display billing form
        st.subheader("Billing Details")
        st.write(f"Email: {email}")
        st.write(f"Order ID: {order_id}")
        st.write(f"Payment ID: {payment_id}")
        st.write(f"Voucher ID: {voucher_id}")
        st.write(f"Final Amount: {final_amount}")
        st.write(f"Status of Payment: {status_of_payment}")

        if st.button("Confirm Billing"):
            # Add billing details to the database
            add_billing(order_id, payment_id, email, voucher_id, final_amount, status_of_payment)
            st.success("Billing successful!")
    else:
        st.error("No order or payment details found. Please proceed to checkout and payment first.")

# Streamlit app
def main():
    
    st.title('Online Retail Application')
    if 'email' not in st.session_state:
        st.session_state.email = None
    
    if 'order_details' not in st.session_state:
        st.session_state.order_details = (None, None)

    if 'selected_item_ids' not in st.session_state:
        st.session_state.selected_item_ids = []
    
    menu = ["Home", "Cart", "Checkout",  "Payment", "Billing Details","View Data",  "Query Operations"]
    page = st.sidebar.selectbox("Menu", menu)
    # page = st.sidebar.radio("Navigation", ["Home", "Cart", "Checkout"])

    if page == "Home":
        st.header("Select an Item")

        # Call the function to load item data
        load_item_data()

        # Fetch categories from the database
        categories = fetch_categories()

        # Display category select box
        selected_category = st.selectbox("Select an Item category:", categories)

        # Fetch items based on selected category
        items = fetch_items_by_category(selected_category)

        # Display radio buttons for each item
        selected_item_id = st.radio("Choose an item:", [f"{item}" for item in items[:50]])

        # Logic to select the item
        if st.button("Add to Cart"):
            if selected_item_id:
                st.session_state.selected_item_ids.append(selected_item_id)
                st.success(f"Item added to cart!")
            else:
                st.warning("Please select an item.")

    elif page == "Cart":
        st.header("My Cart")
        if not st.session_state.selected_item_ids:
            st.write("Your cart is empty.")
        else:
            cart_items_data = []
            for item_id_str in st.session_state.selected_item_ids:
                item_id = ast.literal_eval(item_id_str)[0]  # Extract item ID from the string
                item_data = fetch_item_by_id(item_id)
                if item_data:
                    cart_items_data.append(item_data)
            if cart_items_data:
                st.write("Selected items:")
                st.table(pd.DataFrame(cart_items_data, columns=["Item ID", "Item Name", "Category", "Manufacture Date", "Expiry Date", "Price"]))
                
            else:
                st.write("No items found in the cart.")
        
    elif page == "Checkout":
        add_data()

    elif page == "Payment":
        payment_page()
        
    elif page == "Billing Details":
        billing_page()

    elif page == "View Data":
        view_data()

    elif page== "Query Operations":
        st.subheader('SQL Query Editor')
        query = st.text_area('Enter your SQL query here:', '')

        # Execute the query
        if st.button('Submit Query'):
            try:
                result = pd.read_sql(query, conn)
                st.write('Query Result:')
                st.write(result)
            except Exception as e:
                st.write('Error:', e)

if __name__ == "__main__":
    main()