"""
Vehicle Service Management System
Flask + MySQL Backend
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'vsms_super_secret_2024'

# ── Database Config ──────────────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'database': 'vehicle_service_db',
    'user':     'root',
    'password': 'ksit123',   # ← change this
    'port':     3306
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None


# ══════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════
@app.route('/')
def dashboard():
    conn = get_db()
    if not conn:
        flash('⚠ Cannot connect to database. Check config.', 'error')
        return render_template('dashboard.html', stats={}, recent_orders=[])

    cur = conn.cursor(dictionary=True)

    stats = {}
    queries = {
        'total_customers': "SELECT COUNT(*) c FROM customers",
        'total_vehicles':  "SELECT COUNT(*) c FROM vehicles",
        'pending_orders':  "SELECT COUNT(*) c FROM service_orders WHERE status='pending'",
        'active_orders':   "SELECT COUNT(*) c FROM service_orders WHERE status='in_progress'",
        'completed_orders':"SELECT COUNT(*) c FROM service_orders WHERE status='completed'",
        'total_revenue':   "SELECT COALESCE(SUM(amount),0) c FROM payments WHERE status='paid'",
    }
    for key, q in queries.items():
        cur.execute(q)
        stats[key] = cur.fetchone()['c']

    cur.execute("""
        SELECT so.order_id, c.name customer_name,
               CONCAT(v.make,' ',v.model) vehicle, v.license_plate,
               so.status, so.created_at, so.total_amount
        FROM service_orders so
        JOIN vehicles  v ON so.vehicle_id  = v.vehicle_id
        JOIN customers c ON so.customer_id = c.customer_id
        ORDER BY so.created_at DESC LIMIT 8
    """)
    recent_orders = cur.fetchall()

    cur.execute("""
        SELECT status, COUNT(*) cnt
        FROM service_orders
        GROUP BY status
    """)
    status_counts = {r['status']: r['cnt'] for r in cur.fetchall()}

    cur.close(); conn.close()
    return render_template('dashboard.html', stats=stats,
                           recent_orders=recent_orders, status_counts=status_counts)


# ══════════════════════════════════════════════════════════════
#  CUSTOMERS
# ══════════════════════════════════════════════════════════════
@app.route('/customers')
def customers():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.*, COUNT(v.vehicle_id) vehicle_count
        FROM customers c
        LEFT JOIN vehicles v ON c.customer_id = v.customer_id
        GROUP BY c.customer_id ORDER BY c.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template('customers.html', customers=rows)


@app.route('/customers/add', methods=['POST'])
def add_customer():
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO customers (name,phone,email,address) VALUES (%s,%s,%s,%s)",
            (request.form['name'], request.form['phone'],
             request.form['email'], request.form['address'])
        )
        conn.commit()
        flash('Customer added successfully!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('customers'))


@app.route('/customers/edit/<int:cid>', methods=['POST'])
def edit_customer(cid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE customers SET name=%s,phone=%s,email=%s,address=%s WHERE customer_id=%s",
            (request.form['name'], request.form['phone'],
             request.form['email'], request.form['address'], cid)
        )
        conn.commit()
        flash('Customer updated!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('customers'))


@app.route('/customers/delete/<int:cid>', methods=['POST'])
def delete_customer(cid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM customers WHERE customer_id=%s", (cid,))
        conn.commit()
        flash('Customer deleted.', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('customers'))


# ══════════════════════════════════════════════════════════════
#  VEHICLES
# ══════════════════════════════════════════════════════════════
@app.route('/vehicles')
def vehicles():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT v.*, c.name owner_name, c.phone owner_phone,
               COUNT(so.order_id) service_count
        FROM vehicles v
        JOIN customers c ON v.customer_id = c.customer_id
        LEFT JOIN service_orders so ON v.vehicle_id = so.vehicle_id
        GROUP BY v.vehicle_id ORDER BY v.vehicle_id DESC
    """)
    rows = cur.fetchall()
    cur.execute("SELECT customer_id, name FROM customers ORDER BY name")
    cust = cur.fetchall()
    cur.close(); conn.close()
    return render_template('vehicles.html', vehicles=rows, customers=cust)


@app.route('/vehicles/add', methods=['POST'])
def add_vehicle():
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO vehicles (customer_id,make,model,year,license_plate,color,vin)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (request.form['customer_id'], request.form['make'],
              request.form['model'],       request.form['year'],
              request.form['license_plate'], request.form['color'],
              request.form.get('vin','')))
        conn.commit()
        flash('Vehicle registered!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('vehicles'))


@app.route('/vehicles/delete/<int:vid>', methods=['POST'])
def delete_vehicle(vid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM vehicles WHERE vehicle_id=%s", (vid,))
        conn.commit()
        flash('Vehicle removed.', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('vehicles'))


# ══════════════════════════════════════════════════════════════
#  SERVICES CATALOG
# ══════════════════════════════════════════════════════════════
@app.route('/services')
def services():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT s.*, COUNT(os.id) times_used
        FROM services s
        LEFT JOIN order_services os ON s.service_id = os.service_id
        GROUP BY s.service_id ORDER BY s.name
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template('services.html', services=rows)


@app.route('/services/add', methods=['POST'])
def add_service():
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO services (name,description,price,duration_hours) VALUES (%s,%s,%s,%s)",
            (request.form['name'], request.form['description'],
             request.form['price'], request.form['duration_hours'])
        )
        conn.commit()
        flash('Service added!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('services'))


@app.route('/services/edit/<int:sid>', methods=['POST'])
def edit_service(sid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE services SET name=%s,description=%s,price=%s,duration_hours=%s WHERE service_id=%s",
            (request.form['name'], request.form['description'],
             request.form['price'], request.form['duration_hours'], sid)
        )
        conn.commit()
        flash('Service updated!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('services'))


@app.route('/services/delete/<int:sid>', methods=['POST'])
def delete_service(sid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM services WHERE service_id=%s", (sid,))
        conn.commit()
        flash('Service removed.', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('services'))


# ══════════════════════════════════════════════════════════════
#  MECHANICS
# ══════════════════════════════════════════════════════════════
@app.route('/mechanics')
def mechanics():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT m.*,
               COUNT(CASE WHEN so.status IN ('pending','in_progress') THEN 1 END) active_jobs,
               COUNT(so.order_id) total_jobs
        FROM mechanics m
        LEFT JOIN service_orders so ON m.mechanic_id = so.mechanic_id
        GROUP BY m.mechanic_id ORDER BY m.name
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template('mechanics.html', mechanics=rows)


@app.route('/mechanics/add', methods=['POST'])
def add_mechanic():
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO mechanics (name,phone,specialization,status) VALUES (%s,%s,%s,%s)",
            (request.form['name'], request.form['phone'],
             request.form['specialization'], request.form.get('status','available'))
        )
        conn.commit()
        flash('Mechanic added!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('mechanics'))


@app.route('/mechanics/edit/<int:mid>', methods=['POST'])
def edit_mechanic(mid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE mechanics SET name=%s,phone=%s,specialization=%s,status=%s WHERE mechanic_id=%s",
            (request.form['name'], request.form['phone'],
             request.form['specialization'], request.form['status'], mid)
        )
        conn.commit()
        flash('Mechanic updated!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('mechanics'))


@app.route('/mechanics/delete/<int:mid>', methods=['POST'])
def delete_mechanic(mid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM mechanics WHERE mechanic_id=%s", (mid,))
        conn.commit()
        flash('Mechanic removed.', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('mechanics'))


# ══════════════════════════════════════════════════════════════
#  SERVICE ORDERS
# ══════════════════════════════════════════════════════════════
@app.route('/orders')
def orders():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT so.*,
               c.name customer_name,
               CONCAT(v.make,' ',v.model,' (',v.license_plate,')') vehicle_info,
               m.name mechanic_name
        FROM service_orders so
        JOIN customers c  ON so.customer_id = c.customer_id
        JOIN vehicles  v  ON so.vehicle_id  = v.vehicle_id
        LEFT JOIN mechanics m ON so.mechanic_id = m.mechanic_id
        ORDER BY so.created_at DESC
    """)
    rows = cur.fetchall()

    cur.execute("SELECT customer_id, name FROM customers ORDER BY name")
    custs = cur.fetchall()
    cur.execute("SELECT vehicle_id, customer_id, make, model, license_plate FROM vehicles")
    vehs  = cur.fetchall()
    cur.execute("SELECT mechanic_id, name FROM mechanics WHERE status!='off' ORDER BY name")
    mechs = cur.fetchall()
    cur.execute("SELECT service_id, name, price FROM services ORDER BY name")
    svcs  = cur.fetchall()

    cur.close(); conn.close()
    return render_template('orders.html', orders=rows, customers=custs,
                           vehicles=vehs, mechanics=mechs, services=svcs)


@app.route('/orders/add', methods=['POST'])
def add_order():
    conn = get_db(); cur = conn.cursor()
    try:
        sids = request.form.getlist('service_ids')
        total = 0.0
        if sids:
            ph = ','.join(['%s']*len(sids))
            cur.execute(f"SELECT SUM(price) s FROM services WHERE service_id IN ({ph})", sids)
            r = cur.fetchone(); total = float(r[0]) if r[0] else 0.0

        mechanic_id = request.form.get('mechanic_id') or None

        cur.execute("""
            INSERT INTO service_orders (vehicle_id,customer_id,mechanic_id,status,notes,total_amount)
            VALUES (%s,%s,%s,'pending',%s,%s)
        """, (request.form['vehicle_id'], request.form['customer_id'],
              mechanic_id, request.form.get('notes',''), total))
        oid = cur.lastrowid

        for sid in sids:
            cur.execute("SELECT price FROM services WHERE service_id=%s", (sid,))
            p = cur.fetchone()[0]
            cur.execute("INSERT INTO order_services (order_id,service_id,price) VALUES (%s,%s,%s)",
                        (oid, sid, p))

        conn.commit()
        flash(f'Order #{oid} created!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('orders'))


@app.route('/orders/<int:oid>')
def order_detail(oid):
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT so.*, c.name customer_name, c.phone customer_phone, c.email customer_email,
               v.make, v.model, v.year, v.license_plate, v.color,
               m.name mechanic_name, m.phone mechanic_phone
        FROM service_orders so
        JOIN customers c ON so.customer_id = c.customer_id
        JOIN vehicles  v ON so.vehicle_id  = v.vehicle_id
        LEFT JOIN mechanics m ON so.mechanic_id = m.mechanic_id
        WHERE so.order_id=%s
    """, (oid,))
    order = cur.fetchone()

    cur.execute("""
        SELECT s.name, s.description, os.price
        FROM order_services os
        JOIN services s ON os.service_id = s.service_id
        WHERE os.order_id=%s
    """, (oid,))
    svc_list = cur.fetchall()

    cur.execute("SELECT * FROM payments WHERE order_id=%s ORDER BY payment_date DESC", (oid,))
    pmts = cur.fetchall()

    cur.execute("SELECT mechanic_id, name, status FROM mechanics ORDER BY name")
    mechs = cur.fetchall()

    cur.close(); conn.close()
    return render_template('order_detail.html', order=order,
                           order_services=svc_list, payments=pmts, mechanics=mechs)


@app.route('/orders/update/<int:oid>', methods=['POST'])
def update_order(oid):
    conn = get_db(); cur = conn.cursor()
    try:
        status = request.form['status']
        mid    = request.form.get('mechanic_id') or None
        notes  = request.form.get('notes', '')
        if status == 'completed':
            cur.execute("""
                UPDATE service_orders
                SET status=%s, mechanic_id=%s, notes=%s, completed_at=NOW()
                WHERE order_id=%s
            """, (status, mid, notes, oid))
        else:
            cur.execute("""
                UPDATE service_orders
                SET status=%s, mechanic_id=%s, notes=%s
                WHERE order_id=%s
            """, (status, mid, notes, oid))
        conn.commit()
        flash('Order updated!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('order_detail', oid=oid))


@app.route('/orders/delete/<int:oid>', methods=['POST'])
def delete_order(oid):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM order_services WHERE order_id=%s", (oid,))
        cur.execute("DELETE FROM payments WHERE order_id=%s", (oid,))
        cur.execute("DELETE FROM service_orders WHERE order_id=%s", (oid,))
        conn.commit()
        flash('Order deleted.', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('orders'))


# ══════════════════════════════════════════════════════════════
#  PAYMENTS
# ══════════════════════════════════════════════════════════════
@app.route('/payments')
def payments():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, c.name customer_name,
               CONCAT(v.make,' ',v.model) vehicle_info,
               so.total_amount order_total
        FROM payments p
        JOIN service_orders so ON p.order_id = so.order_id
        JOIN customers c ON so.customer_id = c.customer_id
        JOIN vehicles  v ON so.vehicle_id  = v.vehicle_id
        ORDER BY p.payment_date DESC
    """)
    pmts = cur.fetchall()

    cur.execute("""
        SELECT so.order_id, c.name customer_name,
               CONCAT(v.make,' ',v.model,' (',v.license_plate,')') vehicle_info,
               so.total_amount,
               COALESCE(SUM(p.amount),0) paid_amount
        FROM service_orders so
        JOIN customers c ON so.customer_id = c.customer_id
        JOIN vehicles  v ON so.vehicle_id  = v.vehicle_id
        LEFT JOIN payments p ON so.order_id = p.order_id AND p.status='paid'
        WHERE so.status='completed'
        GROUP BY so.order_id
        HAVING paid_amount < so.total_amount
    """)
    pending = cur.fetchall()

    cur.close(); conn.close()
    return render_template('payments.html', payments=pmts, pending_payments=pending)


@app.route('/payments/add', methods=['POST'])
def add_payment():
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO payments (order_id,amount,payment_method,status) VALUES (%s,%s,%s,'paid')",
            (request.form['order_id'], request.form['amount'], request.form['payment_method'])
        )
        conn.commit()
        flash('Payment recorded!', 'success')
    except Error as e:
        flash(f'Error: {e}', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('payments'))


# ══════════════════════════════════════════════════════════════
#  API helpers
# ══════════════════════════════════════════════════════════════
@app.route('/api/vehicles/<int:cid>')
def api_vehicles(cid):
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT vehicle_id,make,model,license_plate FROM vehicles WHERE customer_id=%s", (cid,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
