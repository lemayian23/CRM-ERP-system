from config.database import get_db

def get_dashboard_metrics():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    metrics = {}
    
    # 1. Job Card Metrics
    cursor.execute("SELECT COUNT(*) as count FROM tbl_job_card WHERE status = 'pending' AND is_closed = 0")
    metrics['unassigned_jc'] = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM tbl_job_card WHERE status = 'active' AND is_closed = 0 AND is_paid = 0")
    metrics['running_jc'] = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM tbl_job_card WHERE proposed_date < CURDATE() AND is_closed = 0")
    metrics['past_planned_jc'] = cursor.fetchone()['count']
    
    # 2. Financial Metrics
    cursor.execute("SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total FROM tbl_job_card WHERE is_closed = 1 AND is_paid = 0")
    pending = cursor.fetchone()
    metrics['pending_payment_count'] = pending['count']
    metrics['pending_payment_total'] = float(pending['total'])
    
    # 3. Customer Metrics
    cursor.execute("SELECT customer_type, COUNT(*) as count FROM tbl_customer GROUP BY customer_type")
    customers = cursor.fetchall()
    metrics['customers'] = {c['customer_type']: c['count'] for c in customers}
    
    # 4. Project Metrics
    cursor.execute("SELECT COUNT(*) as count FROM tbl_project WHERE status = 'running'")
    metrics['running_projects'] = cursor.fetchone()['count']
    
    # 5. Inventory Metrics
    cursor.execute("SELECT COUNT(*) as count FROM tbl_business_unit")
    metrics['business_units'] = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM tbl_brand")
    metrics['brands'] = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM tbl_category")
    metrics['categories'] = cursor.fetchone()['count']
    
    # 6. Stock Valuation
    cursor.execute("SELECT COALESCE(SUM(quantity * purchase_price), 0) as total FROM tbl_item")
    metrics['items_value'] = float(cursor.fetchone()['total'])
    
    cursor.execute("SELECT COALESCE(SUM(quantity * purchase_price), 0) as total FROM tbl_product")
    metrics['products_value'] = float(cursor.fetchone()['total'])
    
    cursor.close()
    conn.close()
    
    return metrics