import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )

def init_db():
    """Create all tables if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Admin table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_admin (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            user_type VARCHAR(50) NOT NULL,
            email VARCHAR(150),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Customer table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_customer (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(200),
            customer_type ENUM('Individual', 'Company', 'Reseller') DEFAULT 'Individual',
            email VARCHAR(150),
            phone VARCHAR(50),
            jc_number VARCHAR(50),
            last_jc_date DATE,
            next_call_date DATE,
            frequency INT DEFAULT 30,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Technician table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_technician (
            tech_id INT AUTO_INCREMENT PRIMARY KEY,
            tech_name VARCHAR(100),
            email VARCHAR(150),
            phone VARCHAR(50),
            status VARCHAR(50) DEFAULT 'active'
        )
    """)
    
    # Job Card table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_service_jc (
            id INT AUTO_INCREMENT PRIMARY KEY,
            jc_number VARCHAR(50) UNIQUE,
            jc_type VARCHAR(50),
            customer_type VARCHAR(50),
            customer_name VARCHAR(200),
            customer_id INT,
            jc_assigned_to VARCHAR(100),
            proposed_work_date DATE,
            time_slot VARCHAR(50),
            work_statement TEXT,
            job_finding TEXT,
            amount DECIMAL(10,2),
            total_paid_amount DECIMAL(10,2) DEFAULT 0,
            payment_type VARCHAR(50),
            payment_code VARCHAR(100),
            payment_date DATE,
            jc_closed VARCHAR(20),
            paid VARCHAR(20),
            work_done_date DATE,
            hours DECIMAL(5,2),
            material_cost DECIMAL(10,2),
            total_cost DECIMAL(10,2),
            percent_cost DECIMAL(5,2),
            jc_create_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Job Card Items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_service_jc_item (
            id INT AUTO_INCREMENT PRIMARY KEY,
            service_jc_id INT,
            item_id INT,
            item_name VARCHAR(200),
            item_quantity INT,
            total_purchase_cost DECIMAL(10,2),
            FOREIGN KEY (service_jc_id) REFERENCES tbl_service_jc(id)
        )
    """)
    
    # Item table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_item (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(200),
            stock_qty INT DEFAULT 0,
            auto_purchase_price DECIMAL(10,2)
        )
    """)
    
    # Product table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_product (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200),
            stock_qty INT DEFAULT 0,
            auto_purchase_price DECIMAL(10,2)
        )
    """)
    
    # Project table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_project (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_name VARCHAR(200),
            close_project VARCHAR(20)
        )
    """)
    
    # Mpesa numbers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_mpesa_number (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            number VARCHAR(50)
        )
    """)
    
    # Insert default admin
    cursor.execute("SELECT COUNT(*) FROM tbl_admin WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO tbl_admin (username, password, user_type, email)
            VALUES ('admin', 'admin123', 'admin', 'admin@aquashine.com')
        """)
    
    # Insert sample data
    cursor.execute("SELECT COUNT(*) FROM tbl_customer")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO tbl_customer (customer_name, customer_type) VALUES (%s, %s)",
            [('John Doe', 'Individual'), ('ABC Corp', 'Company'), ('Tech Solutions', 'Reseller')])
    
    cursor.execute("SELECT COUNT(*) FROM tbl_item")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO tbl_item (item_name, stock_qty, auto_purchase_price) VALUES (%s, %s, %s)",
            [('Filter', 100, 50.00), ('Pipe', 50, 75.00)])
    
    cursor.execute("SELECT COUNT(*) FROM tbl_product")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO tbl_product (name, stock_qty, auto_purchase_price) VALUES (%s, %s, %s)",
            [('Water Pump', 200, 2500.00), ('Hose', 150, 30.00)])
    
    conn.commit()
    cursor.close()
    conn.close()