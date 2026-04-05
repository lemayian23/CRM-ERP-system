import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    # For TiDB Cloud Serverless - SSL is required
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 4000)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'test'),
        use_pure=True,
        ssl_disabled=False,  # Enable SSL (required for TiDB Cloud)
        ssl_verify_cert=False,  # Don't verify cert for now
        ssl_verify_identity=False
    )

def init_db():
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
    
    # Insert default admin
    cursor.execute("SELECT COUNT(*) FROM tbl_admin WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO tbl_admin (username, password, user_type, email)
            VALUES ('admin', 'admin123', 'admin', 'admin@aquashine.com')
        """)
    
    # Customer table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_customer (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
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
            product_id INT,
            item_name VARCHAR(200),
            product_name VARCHAR(200),
            item_quantity INT,
            product_quantity INT,
            total_purchase_cost DECIMAL(10,2),
            FOREIGN KEY (service_jc_id) REFERENCES tbl_service_jc(id)
        )
    """)
    
    # Item table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_item (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(200),
            quantity INT DEFAULT 0,
            purchase_price DECIMAL(10,2)
        )
    """)
    
    # Product table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_product (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(200),
            quantity INT DEFAULT 0,
            purchase_price DECIMAL(10,2)
        )
    """)
    
    # Project table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_project (
            project_id INT AUTO_INCREMENT PRIMARY KEY,
            project_name VARCHAR(200),
            description TEXT,
            start_date DATE,
            end_date DATE,
            status VARCHAR(50),
            budget DECIMAL(12,2),
            customer_id INT,
            assigned_to VARCHAR(100),
            close_project VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # Stock movement tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_stock_movement_item (
            movement_id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT,
            item_name VARCHAR(200),
            movement_type VARCHAR(20),
            quantity INT,
            previous_quantity INT,
            new_quantity INT,
            reference_type VARCHAR(50),
            reference_id INT,
            notes TEXT,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_stock_movement_product (
            movement_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT,
            product_name VARCHAR(200),
            movement_type VARCHAR(20),
            quantity INT,
            previous_quantity INT,
            new_quantity INT,
            reference_type VARCHAR(50),
            reference_id INT,
            notes TEXT,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Categories, Brands, Subcategories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_category (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_brand (
            brand_id INT AUTO_INCREMENT PRIMARY KEY,
            brand_name VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_subcategory (
            subcategory_id INT AUTO_INCREMENT PRIMARY KEY,
            subcategory_name VARCHAR(100),
            category_id INT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_business (
            business_id INT AUTO_INCREMENT PRIMARY KEY,
            business_name VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Rates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_rates (
            rate_id INT AUTO_INCREMENT PRIMARY KEY,
            rate_name VARCHAR(100),
            rate_type VARCHAR(20),
            amount DECIMAL(10,2),
            description TEXT,
            status VARCHAR(20),
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Service Calls table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_service_calls (
            call_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(200),
            customer_phone VARCHAR(50),
            call_date DATE,
            issue_description TEXT,
            priority VARCHAR(20),
            status VARCHAR(20),
            assigned_to VARCHAR(100),
            resolution_notes TEXT,
            resolved_date DATE,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # AMC tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_amc (
            amc_id INT AUTO_INCREMENT PRIMARY KEY,
            amc_number VARCHAR(50),
            customer_id INT,
            customer_name VARCHAR(200),
            contract_start DATE,
            contract_end DATE,
            contract_value DECIMAL(12,2),
            payment_terms VARCHAR(100),
            service_level VARCHAR(100),
            status VARCHAR(20),
            notes TEXT,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_amc_jc (
            amc_jc_id INT AUTO_INCREMENT PRIMARY KEY,
            amc_id INT,
            jc_id INT,
            visit_date DATE,
            technician_name VARCHAR(100),
            work_done TEXT,
            status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Areas and Commerce
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_area (
            area_id INT AUTO_INCREMENT PRIMARY KEY,
            area_name VARCHAR(100),
            zone VARCHAR(50),
            distance_km DECIMAL(8,2),
            travel_cost DECIMAL(10,2),
            status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_commerce (
            commerce_id INT AUTO_INCREMENT PRIMARY KEY,
            commerce_name VARCHAR(100),
            area_id INT,
            address TEXT,
            contact_person VARCHAR(100),
            phone VARCHAR(50),
            email VARCHAR(150),
            status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sales Agents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_sales_agents (
            agent_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_name VARCHAR(100),
            email VARCHAR(150),
            phone VARCHAR(50),
            commission_rate DECIMAL(5,2),
            target_amount DECIMAL(12,2),
            achieved_amount DECIMAL(12,2),
            status VARCHAR(20),
            hire_date DATE,
            notes TEXT,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Planner
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_planner (
            event_id INT AUTO_INCREMENT PRIMARY KEY,
            event_title VARCHAR(200),
            event_description TEXT,
            event_date DATE,
            event_time TIME,
            end_date DATE,
            event_type VARCHAR(20),
            related_jc_id INT,
            assigned_to VARCHAR(100),
            status VARCHAR(20),
            color VARCHAR(20),
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Daily Status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_daily_status (
            report_id INT AUTO_INCREMENT PRIMARY KEY,
            report_date DATE UNIQUE,
            total_jobs INT DEFAULT 0,
            new_jobs INT DEFAULT 0,
            closed_jobs INT DEFAULT 0,
            paid_jobs INT DEFAULT 0,
            pending_payment_amount DECIMAL(12,2) DEFAULT 0,
            total_revenue DECIMAL(12,2) DEFAULT 0,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Audit Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_audit_log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            username VARCHAR(100),
            action VARCHAR(50),
            table_name VARCHAR(50),
            record_id INT,
            old_values TEXT,
            new_values TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Suppliers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_supplier (
            supplier_id INT AUTO_INCREMENT PRIMARY KEY,
            supplier_name VARCHAR(200),
            contact_person VARCHAR(100),
            email VARCHAR(150),
            phone VARCHAR(50),
            address TEXT,
            payment_terms VARCHAR(100),
            status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Purchase Orders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_purchase_order (
            po_id INT AUTO_INCREMENT PRIMARY KEY,
            po_number VARCHAR(50) UNIQUE,
            supplier_id INT,
            supplier_name VARCHAR(200),
            order_date DATE,
            expected_delivery DATE,
            status VARCHAR(20),
            total_amount DECIMAL(12,2),
            notes TEXT,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_purchase_order_item (
            po_item_id INT AUTO_INCREMENT PRIMARY KEY,
            po_id INT,
            item_type VARCHAR(20),
            item_id INT,
            item_name VARCHAR(200),
            quantity INT,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2),
            received_quantity INT DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_material_received (
            receive_id INT AUTO_INCREMENT PRIMARY KEY,
            po_id INT,
            po_number VARCHAR(50),
            supplier_id INT,
            supplier_name VARCHAR(200),
            receive_date DATE,
            item_type VARCHAR(20),
            item_id INT,
            item_name VARCHAR(200),
            quantity_received INT,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2),
            received_by VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Quotations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_quotation (
            quote_id INT AUTO_INCREMENT PRIMARY KEY,
            quote_number VARCHAR(50) UNIQUE,
            customer_id INT,
            customer_name VARCHAR(200),
            customer_email VARCHAR(150),
            customer_phone VARCHAR(50),
            quote_date DATE,
            expiry_date DATE,
            subtotal DECIMAL(12,2),
            cost_price DECIMAL(12,2),
            gross_profit DECIMAL(12,2),
            margin_percentage DECIMAL(5,2),
            tax_rate DECIMAL(5,2),
            tax_amount DECIMAL(12,2),
            discount_amount DECIMAL(12,2),
            total_amount DECIMAL(12,2),
            notes TEXT,
            terms_conditions TEXT,
            status VARCHAR(20),
            converted_jc_id INT,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_quotation_item (
            quote_item_id INT AUTO_INCREMENT PRIMARY KEY,
            quote_id INT,
            item_type VARCHAR(20),
            item_id INT,
            item_name VARCHAR(200),
            quantity INT,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2)
        )
    """)
    
    # Insert default admin if not exists
    cursor.execute("SELECT COUNT(*) FROM tbl_admin WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO tbl_admin (username, password, user_type, email)
            VALUES ('admin', 'admin123', 'admin', 'admin@aquashine.com')
        """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()