from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_perpustakaan_modern'

# Kredensial Statis Pustakawan
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'


def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


# ==========================================
# RUTE AUTH (LOGIN & LOGOUT)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Berhasil login sebagai Pustakawan.', 'success')
            return redirect(url_for('pustakawan'))
        else:
            flash('Username atau password salah!', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Anda telah berhasil logout.', 'success')
    return redirect(url_for('index'))


# ==========================================
# RUTE PUSTAKAWAN (DILINDUNGI SESSION)
# ==========================================
@app.route('/pustakawan', methods=['GET', 'POST'])
def pustakawan():
    # Cek apakah pengguna sudah login
    if not session.get('logged_in'):
        flash('Akses ditolak. Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        conn.execute('INSERT INTO books (title, author) VALUES (?, ?)', (title, author))
        conn.commit()
        flash(f'Buku "{title}" berhasil ditambahkan ke inventaris!', 'success')
        return redirect(url_for('pustakawan'))

    books = conn.execute('SELECT * FROM books').fetchall()
    borrowings = conn.execute('''
                              SELECT borrowings.id, borrowings.borrower_name, borrowings.status, books.title
                              FROM borrowings
                                       JOIN books ON borrowings.book_id = books.id
                              ''').fetchall()

    conn.close()
    return render_template('pustakawan.html', books=books, borrowings=borrowings)


@app.route('/return_book/<int:borrow_id>/<int:book_id>')
def return_book(borrow_id, book_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('UPDATE borrowings SET status = "Dikembalikan" WHERE id = ?', (borrow_id,))
    conn.execute('UPDATE books SET is_available = 1 WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    flash('Buku telah dikembalikan dan tersedia kembali.', 'success')
    return redirect(url_for('pustakawan'))


# ==========================================
# RUTE PEMINJAM
# ==========================================
@app.route('/peminjam')
def peminjam():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books WHERE is_available = 1').fetchall()
    conn.close()
    return render_template('peminjam.html', books=books)


@app.route('/borrow_book/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    borrower_name = request.form['borrower_name']
    conn = get_db_connection()
    conn.execute('INSERT INTO borrowings (book_id, borrower_name) VALUES (?, ?)', (book_id, borrower_name))
    conn.execute('UPDATE books SET is_available = 0 WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    flash(f'Buku berhasil dipinjam oleh {borrower_name}. Selamat membaca!', 'success')
    return redirect(url_for('peminjam'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)