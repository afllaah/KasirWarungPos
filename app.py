from flask import Flask, render_template, request, redirect, session
import sqlite3
import qrcode
from datetime import datetime

app = Flask(__name__)
app.secret_key = "kasir123"

# ================= DATABASE =================
def init_db():

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS transaksi(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            total INTEGER
        )
    ''')

    conn.commit()
    conn.close()

# ================= USER DEFAULT =================
def create_admin():

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    user = c.execute(
        "SELECT * FROM user WHERE username='admin'"
    ).fetchone()

    if not user:
        c.execute(
            "INSERT INTO user VALUES(NULL,'admin','1234')"
        )

    conn.commit()
    conn.close()

init_db()
create_admin()

# ================= LOGIN =================
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        user = c.execute(
            "SELECT * FROM user WHERE username=? AND password=?",
            (username,password)
        ).fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/')

        else:
            return "Login gagal"

    return render_template('login.html')

# ================= LOGOUT =================
@app.route('/logout')
def logout():

    session.clear()
    return redirect('/login')

# ================= MENU =================
MENU = [

    # MAKANAN
    {"nama":"Nasi Goreng","harga":15000},
    {"nama":"Mie Goreng","harga":12000},
    {"nama":"Ayam Geprek","harga":18000},
    {"nama":"Ayam Bakar","harga":20000},
    {"nama":"Ayam Penyet","harga":17000},
    {"nama":"Lele Goreng","harga":14000},
    {"nama":"Nasi Ayam Crispy","harga":18000},
    {"nama":"Bakso","harga":13000},
    {"nama":"Soto Ayam","harga":12000},
    {"nama":"Seblak","harga":10000},
    {"nama":"Martabak Telur","harga":15000},
    {"nama":"Nasi Kebuli","harga":25000},
    {"nama":"Burger","harga":17000},
    {"nama":"Kentang Goreng","harga":12000},
    {"nama":"Spaghetti","harga":20000},

    # MINUMAN
    {"nama":"Es Teh","harga":5000},
    {"nama":"Teh Hangat","harga":4000},
    {"nama":"Es Jeruk","harga":7000},
    {"nama":"Jeruk Hangat","harga":6000},
    {"nama":"Kopi Hitam","harga":7000},
    {"nama":"Cappuccino","harga":12000},
    {"nama":"Matcha Latte","harga":15000},
    {"nama":"Thai Tea","harga":12000},
    {"nama":"Milkshake Coklat","harga":15000},
    {"nama":"Air Mineral","harga":4000},

    # SNACK
    {"nama":"Roti Bakar","harga":10000},
    {"nama":"Pisang Coklat","harga":12000},
    {"nama":"Cireng","harga":8000},
    {"nama":"Tahu Crispy","harga":9000},
    {"nama":"Sosis Bakar","harga":10000},
    {"nama":"Dimsum","harga":15000},

]

# ================= HALAMAN KASIR =================
@app.route('/', methods=['GET','POST'])
def index():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        names = request.form.getlist('nama')
        prices = request.form.getlist('harga')
        qtys = request.form.getlist('qty')

        bayar = int(request.form['bayar'])

        total = 0
        items = []

        for i in range(len(names)):

            qty = int(qtys[i]) if qtys[i] else 0
            harga = int(prices[i])

            subtotal = harga * qty
            total += subtotal

            if qty > 0:
                items.append({
                    'nama': names[i],
                    'qty': qty,
                    'subtotal': subtotal
                })

        kembalian = bayar - total

        # simpan transaksi
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        tanggal = datetime.now().strftime("%d-%m-%Y %H:%M")

        c.execute(
            "INSERT INTO transaksi(tanggal,total) VALUES(?,?)",
            (tanggal,total)
        )

        conn.commit()
        conn.close()

        # QR pembayaran
        img = qrcode.make(f"TOTAL BAYAR Rp {total}")
        img.save("static/qr.png")

        return render_template(
            'struk.html',
            items=items,
            total=total,
            bayar=bayar,
            kembalian=kembalian
        )

    return render_template(
        'index.html',
        menu=MENU
    )

# ================= RIWAYAT =================
@app.route('/riwayat')
def riwayat():

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    data = c.execute(
        "SELECT * FROM transaksi ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        'riwayat.html',
        data=data
    )

# ================= RUN =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)