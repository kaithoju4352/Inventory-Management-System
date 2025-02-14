import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox

# --- Database Functions ---
def create_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    
    # Create products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    quantity INTEGER,
                    price REAL)''')
    
    # Create users table (for authentication)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT)''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', (username, hashed_password))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('''SELECT * FROM users WHERE username = ? AND password = ?''', (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user is not None

def add_product(name, quantity, price):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)''', (name, quantity, price))
    conn.commit()
    conn.close()

def update_product(id, name, quantity, price):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''UPDATE products SET name = ?, quantity = ?, price = ? WHERE id = ?''', (name, quantity, price, id))
    conn.commit()
    conn.close()

def delete_product(id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''DELETE FROM products WHERE id = ?''', (id,))
    conn.commit()
    conn.close()

def get_inventory():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM products''')
    inventory = c.fetchall()
    conn.close()
    return inventory

def low_stock_alert(threshold):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM products WHERE quantity < ?''', (threshold,))
    low_stock = c.fetchall()
    conn.close()
    return low_stock


# --- GUI Class ---
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("500x400")
        
        self.login_frame = tk.Frame(root)
        self.main_frame = tk.Frame(root)
        
        self.create_login_screen()
    
    def create_login_screen(self):
        self.login_frame.pack()
        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)
        
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)
        
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if authenticate_user(username, password):
            self.login_frame.pack_forget()
            self.create_inventory_screen()
        else:
            messagebox.showerror("Login Error", "Invalid username or password")
    
    def create_inventory_screen(self):
        self.main_frame.pack()
        
        self.add_product_button = tk.Button(self.main_frame, text="Add Product", command=self.add_product_screen)
        self.add_product_button.pack()
        
        self.view_inventory_button = tk.Button(self.main_frame, text="View Inventory", command=self.view_inventory)
        self.view_inventory_button.pack()
        
        self.low_stock_button = tk.Button(self.main_frame, text="Low Stock Alerts", command=self.low_stock)
        self.low_stock_button.pack()
    
    def add_product_screen(self):
        # Create a new window for adding a product
        add_product_window = tk.Toplevel(self.root)
        add_product_window.title("Add Product")
        add_product_window.geometry("300x200")
        
        tk.Label(add_product_window, text="Product Name:").pack()
        product_name_entry = tk.Entry(add_product_window)
        product_name_entry.pack()
        
        tk.Label(add_product_window, text="Quantity:").pack()
        quantity_entry = tk.Entry(add_product_window)
        quantity_entry.pack()
        
        tk.Label(add_product_window, text="Price:").pack()
        price_entry = tk.Entry(add_product_window)
        price_entry.pack()
        
        def save_product():
            name = product_name_entry.get()
            quantity = int(quantity_entry.get())
            price = float(price_entry.get())
            add_product(name, quantity, price)
            add_product_window.destroy()
            messagebox.showinfo("Success", "Product added successfully!")
        
        save_button = tk.Button(add_product_window, text="Save Product", command=save_product)
        save_button.pack()
    
    def view_inventory(self):
        inventory = get_inventory()
        inventory_list = "\n".join([f"{item[1]} - {item[2]} in stock - ${item[3]}" for item in inventory])
        messagebox.showinfo("Inventory", inventory_list)
    
    def low_stock(self):
        low_stock_items = low_stock_alert(5)
        low_stock_list = "\n".join([f"{item[1]} - {item[2]} in stock" for item in low_stock_items])
        messagebox.showinfo("Low Stock Alert", low_stock_list)


if __name__ == "__main__":
    create_db()  # Ensure the database is created before running the app
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
