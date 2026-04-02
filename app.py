from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
import os
from config.database import get_db
from datetime import date

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def get_dashboard_metrics():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    metrics = {
        'unassigned_jc': 0,
        'running_jc': 0,
        'past_planned_jc': 0,
        'pending_payment_count': 0,
        'pending_payment_total': 0,
        'customers': {'Individual': 0, 'Company': 0, 'Reseller': 0},
        'running_projects': 0,
        'items_count': 0,
        'products_count': 0,
        'items_value': 0,
        'products_value': 0
    }
    
    # Unassigned JC
    try:
        cursor.execute("SELECT COUNT(*) as count FROM tbl_service_jc WHERE jc_assigned_to IS NULL OR jc_assigned_to = ''")
        row = cursor.fetchone()
        if row:
            metrics['unassigned_jc'] = row['count']
    except Exception as e:
        print(f"Error in unassigned_jc: {e}")
    
    # Running JC
    try:
        cursor.execute("SELECT COUNT(*) as count FROM tbl_service_jc WHERE jc_assigned_to IS NOT NULL AND jc_assigned_to != '' AND (jc_closed IS NULL OR jc_closed != 'Closed') AND (paid IS NULL OR paid != 'Paid')")
        row = cursor.fetchone()
        if row:
            metrics['running_jc'] = row['count']
    except Exception as e:
        print(f"Error in running_jc: {e}")
    
    # Past Planned JC
    try:
        cursor.execute("SELECT COUNT(*) as count FROM tbl_service_jc WHERE jc_assigned_to IS NOT NULL AND jc_assigned_to != '' AND (jc_closed IS NULL OR jc_closed != 'Closed') AND (paid IS NULL OR paid != 'Paid') AND proposed_work_date < %s", (date.today(),))
        row = cursor.fetchone()
        if row:
            metrics['past_planned_jc'] = row['count']
    except Exception as e:
        print(f"Error in past_planned_jc: {e}")
    
    # Pending Payment
    try:
        cursor.execute("SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM tbl_service_jc WHERE jc_closed = 'Closed' AND (paid IS NULL OR paid != 'Paid')")
        row = cursor.fetchone()
        if row:
            metrics['pending_payment_count'] = row['count']
            metrics['pending_payment_total'] = float(row['total']) if row['total'] else 0
    except Exception as e:
        print(f"Error in pending_payment: {e}")
    
    # Customer metrics
    try:
        cursor.execute("SELECT customer_type, COUNT(*) as count FROM tbl_customer GROUP BY customer_type")
        rows = cursor.fetchall()
        for row in rows:
            if row['customer_type'] in metrics['customers']:
                metrics['customers'][row['customer_type']] = row['count']
    except Exception as e:
        print(f"Error in customers: {e}")
    
    # Running projects
    try:
        cursor.execute("SELECT COUNT(*) as count FROM tbl_project")
        row = cursor.fetchone()
        if row:
            metrics['running_projects'] = row['count']
    except Exception as e:
        print(f"Error in projects: {e}")
    
    # Items count
    try:
        cursor.execute("SELECT COUNT(*) as count FROM tbl_item")
        row = cursor.fetchone()
        if row:
            metrics['items_count'] = row['count']
    except Exception as e:
        print(f"Error in items count: {e}")
    
    # Products count
    try:
        cursor.execute("SELECT COUNT(*) as count FROM tbl_product")
        row = cursor.fetchone()
        if row:
            metrics['products_count'] = row['count']
    except Exception as e:
        print(f"Error in products count: {e}")
    
    # Items value - check if columns exist
    try:
        cursor.execute("SHOW COLUMNS FROM tbl_item")
        columns = [col['Field'] for col in cursor.fetchall()]
        if 'stock_qty' in columns and 'auto_purchase_price' in columns:
            cursor.execute("SELECT COALESCE(SUM(stock_qty * auto_purchase_price), 0) as total FROM tbl_item")
            row = cursor.fetchone()
            if row:
                metrics['items_value'] = float(row['total']) if row['total'] else 0
    except Exception as e:
        print(f"Error in items value: {e}")
    
    # Products value - check if columns exist
    try:
        cursor.execute("SHOW COLUMNS FROM tbl_product")
        columns = [col['Field'] for col in cursor.fetchall()]
        if 'stock_qty' in columns and 'auto_purchase_price' in columns:
            cursor.execute("SELECT COALESCE(SUM(stock_qty * auto_purchase_price), 0) as total FROM tbl_product")
            row = cursor.fetchone()
            if row:
                metrics['products_value'] = float(row['total']) if row['total'] else 0
    except Exception as e:
        print(f"Error in products value: {e}")
    
    cursor.close()
    conn.close()
    
    return metrics

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM tbl_admin WHERE username=%s AND password=%s",
        (request.form['username'], request.form['password'])
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['user_id'] = user['user_id']
        session['user'] = user['user']
        session['username'] = user['username']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Invalid username or password')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    metrics = get_dashboard_metrics()
    return render_template('dashboard.html', 
                         username=session['username'], 
                         role=session['user'],
                         metrics=metrics)

@app.route('/job-cards')
def job_cards():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_service_jc ORDER BY id DESC")
    job_cards = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('job_cards.html', 
                         username=session['username'], 
                         role=session['user'],
                         job_cards=job_cards)


@app.route('/job-cards/create', methods=['GET'])
def create_job_card_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('create_job_card.html', 
                         username=session['username'], 
                         role=session['user'])

@app.route('/job-cards/create', methods=['POST'])
def create_job_card_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tbl_service_jc (jc_type, customer_type, customer_name, customer_id, 
        jc_create_date, amount, work_statement)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        request.form['jc_type'],
        request.form['customer_type'],
        request.form['customer_name'],
        request.form['customer_id'] or None,
        request.form['jc_create_date'],
        request.form['amount'],
        request.form['work_statement']
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('job_cards'))

@app.route('/job-cards/<int:jc_id>/assign', methods=['GET'])
def assign_technician_form(jc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tbl_service_jc WHERE id = %s", (jc_id,))
    job_card = cursor.fetchone()
    
    cursor.execute("SELECT * FROM tbl_technician WHERE status = 'active'")
    technicians = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('assign_technician.html', 
                         username=session['username'], 
                         role=session['user'],
                         job_card=job_card,
                         technicians=technicians)

@app.route('/job-cards/<int:jc_id>/assign', methods=['POST'])
def assign_technician_post(jc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE tbl_service_jc 
        SET jc_assigned_to = %s, proposed_work_date = %s, time_slot = %s
        WHERE id = %s
    """, (request.form['technician'], request.form['proposed_work_date'], request.form['time_slot'], jc_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('job_cards'))


@app.route('/job-cards/<int:jc_id>/close', methods=['GET'])
def close_job_card_form(jc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_service_jc WHERE id = %s", (jc_id,))
    job_card = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('close_job_card.html', 
                         username=session['username'], 
                         role=session['user'],
                         job_card=job_card)

@app.route('/job-cards/<int:jc_id>/close', methods=['POST'])
def close_job_card_post(jc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Update job card as closed
    cursor.execute("""
        UPDATE tbl_service_jc 
        SET jc_closed = 'Closed', job_finding = %s, work_done_date = %s, hours = %s
        WHERE id = %s
    """, (request.form['job_finding'], request.form['work_done_date'], request.form['hours'] or 0, jc_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('job_cards'))


@app.route('/job-cards/<int:jc_id>/payment', methods=['GET'])
def payment_job_card_form(jc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_service_jc WHERE id = %s", (jc_id,))
    job_card = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('payment_job_card.html', 
                         username=session['username'], 
                         role=session['user'],
                         job_card=job_card)

@app.route('/job-cards/<int:jc_id>/payment', methods=['POST'])
def payment_job_card_post(jc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE tbl_service_jc 
        SET paid = 'Paid', payment_type = %s, payment_code = %s, 
            total_paid_amount = %s, payment_date = %s
        WHERE id = %s
    """, (request.form['payment_type'], request.form['payment_code'], 
          request.form['total_paid_amount'], request.form['payment_date'], jc_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('job_cards'))


@app.route('/customers')
def customers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_customer ORDER BY customer_id DESC")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('customers.html', 
                         username=session['username'], 
                         role=session['user'],
                         customers=customers)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tbl_customer (customer_name, customer_type, email, phone)
        VALUES (%s, %s, %s, %s)
    """, (request.form['customer_name'], request.form['customer_type'], 
          request.form['email'], request.form['phone']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('customers'))

@app.route('/customers/edit', methods=['POST'])
def edit_customer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tbl_customer 
        SET customer_name = %s, customer_type = %s, email = %s, phone = %s
        WHERE customer_id = %s
    """, (request.form['customer_name'], request.form['customer_type'], 
          request.form['email'], request.form['phone'], request.form['customer_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('customers'))

@app.route('/customers/delete/<int:customer_id>')
def delete_customer(customer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tbl_customer WHERE customer_id = %s", (customer_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('customers'))


@app.route('/inventory')
def inventory():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_item ORDER BY item_id DESC")
    items = cursor.fetchall()
    cursor.execute("SELECT * FROM tbl_product ORDER BY product_id DESC")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('inventory.html', 
                         username=session['username'], 
                         role=session['user'],
                         items=items,
                         products=products)

@app.route('/inventory/item/add', methods=['POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tbl_item (item_name, quantity, purchase_price)
        VALUES (%s, %s, %s)
    """, (request.form['item_name'], request.form['quantity'], request.form['purchase_price']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/product/add', methods=['POST'])
def add_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tbl_product (product_name, quantity, purchase_price)
        VALUES (%s, %s, %s)
    """, (request.form['product_name'], request.form['quantity'], request.form['purchase_price']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/item/edit', methods=['POST'])
def edit_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tbl_item 
        SET item_name = %s, quantity = %s, purchase_price = %s
        WHERE item_id = %s
    """, (request.form['item_name'], request.form['quantity'], 
          request.form['purchase_price'], request.form['item_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/product/edit', methods=['POST'])
def edit_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tbl_product 
        SET product_name = %s, quantity = %s, purchase_price = %s
        WHERE product_id = %s
    """, (request.form['product_name'], request.form['quantity'], 
          request.form['purchase_price'], request.form['product_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/item/delete/<int:item_id>')
def delete_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tbl_item WHERE item_id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/product/delete/<int:product_id>')
def delete_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tbl_product WHERE product_id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('inventory'))   


@app.route('/technicians')
def technicians():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_technician ORDER BY tech_id DESC")
    technicians = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('technicians.html', 
                         username=session['username'], 
                         role=session['user'],
                         technicians=technicians)

@app.route('/technicians/add', methods=['POST'])
def add_technician():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tbl_technician (tech_name, email, phone, status)
        VALUES (%s, %s, %s, %s)
    """, (request.form['tech_name'], request.form['email'], 
          request.form['phone'], request.form['status']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('technicians'))

@app.route('/technicians/edit', methods=['POST'])
def edit_technician():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tbl_technician 
        SET tech_name = %s, email = %s, phone = %s, status = %s
        WHERE tech_id = %s
    """, (request.form['tech_name'], request.form['email'], 
          request.form['phone'], request.form['status'], request.form['tech_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('technicians'))

@app.route('/technicians/delete/<int:tech_id>')
def delete_technician(tech_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tbl_technician WHERE tech_id = %s", (tech_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('technicians'))


# ============ REPORTS MODULE ============

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('reports.html', 
                         username=session['username'], 
                         role=session['user'])

@app.route('/reports/financial')
def financial_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    period = request.args.get('period', 'all')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Date filter logic
    date_filter = ""
    if period == 'week':
        date_filter = "AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    elif period == 'month':
        date_filter = "AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
    elif period == 'year':
        date_filter = "AND created_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)"
    
    # Get all payments with date filter
    cursor.execute(f"""
        SELECT * FROM tbl_service_jc 
        WHERE 1=1 {date_filter}
        ORDER BY created_at DESC
    """)
    payments = cursor.fetchall()
    
    # Calculate summary
    cursor.execute(f"""
        SELECT 
            COALESCE(SUM(CASE WHEN paid = 'Paid' THEN total_paid_amount ELSE amount END), 0) as total_revenue,
            COALESCE(SUM(CASE WHEN paid != 'Paid' AND jc_closed = 'Closed' THEN amount ELSE 0 END), 0) as pending_amount,
            COUNT(CASE WHEN paid = 'Paid' THEN 1 END) as paid_count,
            COUNT(*) as total_jobs,
            COUNT(CASE WHEN paid != 'Paid' AND jc_closed = 'Closed' THEN 1 END) as pending_count
        FROM tbl_service_jc
        WHERE 1=1 {date_filter}
    """)
    summary = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('financial_report.html',
                         username=session['username'],
                         role=session['user'],
                         payments=payments,
                         summary=summary)

                         
@app.route('/reports/job-cards')
def job_card_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM tbl_service_jc 
        ORDER BY created_at DESC
    """)
    job_cards = cursor.fetchall()
    
    # Summary statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN jc_closed = 'Closed' THEN 1 ELSE 0 END) as closed,
            SUM(CASE WHEN jc_closed IS NULL OR jc_closed != 'Closed' THEN 1 ELSE 0 END) as open,
            SUM(CASE WHEN paid = 'Paid' THEN 1 ELSE 0 END) as paid,
            SUM(CASE WHEN paid != 'Paid' THEN 1 ELSE 0 END) as unpaid
        FROM tbl_service_jc
    """)
    summary = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('job_card_report.html',
                         username=session['username'],
                         role=session['user'],
                         job_cards=job_cards,
                         summary=summary)

@app.route('/reports/stock')
def stock_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tbl_item ORDER BY item_name")
    items = cursor.fetchall()
    
    cursor.execute("SELECT * FROM tbl_product ORDER BY product_name")
    products = cursor.fetchall()
    
    # Calculate total stock value
    cursor.execute("SELECT COALESCE(SUM(quantity * purchase_price), 0) as total FROM tbl_item")
    items_total = cursor.fetchone()
    cursor.execute("SELECT COALESCE(SUM(quantity * purchase_price), 0) as total FROM tbl_product")
    products_total = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('stock_report.html',
                         username=session['username'],
                         role=session['user'],
                         items=items,
                         products=products,
                         items_total=items_total['total'],
                         products_total=products_total['total'])

@app.route('/reports/customers')
def customer_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, 
               COUNT(jc.id) as total_jobs,
               SUM(CASE WHEN jc.paid = 'Paid' THEN jc.amount ELSE 0 END) as total_spent
        FROM tbl_customer c
        LEFT JOIN tbl_service_jc jc ON c.customer_name = jc.customer_name
        GROUP BY c.customer_id
        ORDER BY c.customer_name
    """)
    customers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customer_report.html',
                         username=session['username'],
                         role=session['user'],
                         customers=customers)

@app.route('/reports/technicians')
def technician_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT t.*, 
               COUNT(jc.id) as total_jobs,
               SUM(CASE WHEN jc.paid = 'Paid' THEN jc.amount ELSE 0 END) as revenue,
               SUM(CASE WHEN jc.jc_closed = 'Closed' THEN 1 ELSE 0 END) as completed_jobs
        FROM tbl_technician t
        LEFT JOIN tbl_service_jc jc ON t.tech_name = jc.jc_assigned_to
        GROUP BY t.tech_id
        ORDER BY t.tech_name
    """)
    technicians = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('technician_report.html',
                         username=session['username'],
                         role=session['user'],
                         technicians=technicians)


# ============ MPESA NUMBER MANAGEMENT ============

@app.route('/mpesa')
def mpesa_numbers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_mpesa_number ORDER BY id DESC")
    mpesa_numbers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('mpesa.html',
                         username=session['username'],
                         role=session['user'],
                         mpesa_numbers=mpesa_numbers)

@app.route('/mpesa/add', methods=['POST'])
def add_mpesa():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tbl_mpesa_number (name, number) VALUES (%s, %s)",
                   (request.form['name'], request.form['number']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('mpesa_numbers'))

@app.route('/mpesa/edit', methods=['POST'])
def edit_mpesa():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tbl_mpesa_number SET name = %s, number = %s WHERE id = %s",
                   (request.form['name'], request.form['number'], request.form['id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('mpesa_numbers'))

@app.route('/mpesa/delete/<int:mpesa_id>')
def delete_mpesa(mpesa_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tbl_mpesa_number WHERE id = %s", (mpesa_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('mpesa_numbers'))                       

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)