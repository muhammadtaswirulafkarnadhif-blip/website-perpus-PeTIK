import sqlite3


def init_db():
    # Menghubungkan ke database (akan terbuat otomatis jika belum ada)
    conn = sqlite3.connect('library.db')

    # Mengaktifkan mode WAL untuk performa baca/tulis yang lebih baik
    conn.execute('PRAGMA journal_mode=WAL;')
    cursor = conn.cursor()

    # Membuat tabel buku
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS books
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       author
                       TEXT
                       NOT
                       NULL,
                       is_available
                       BOOLEAN
                       NOT
                       NULL
                       DEFAULT
                       1
                   )
                   ''')

    # Membuat tabel peminjaman
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS borrowings
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       book_id
                       INTEGER
                       NOT
                       NULL,
                       borrower_name
                       TEXT
                       NOT
                       NULL,
                       status
                       TEXT
                       NOT
                       NULL
                       DEFAULT
                       'Dipinjam',
                       FOREIGN
                       KEY
                   (
                       book_id
                   ) REFERENCES books
                   (
                       id
                   )
                       )
                   ''')

    # Memasukkan data awal jika database masih kosong
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        buku_awal = [
            ('Algoritma dan Pemrograman', 'Rinaldi Munir', 1),
            ('Clean Code', 'Robert C. Martin', 1),
            ('Desain UI/UX Modern', 'Gary Simon', 1)
        ]
        cursor.executemany('INSERT INTO books (title, author, is_available) VALUES (?, ?, ?)', buku_awal)

    conn.commit()
    conn.close()
    print("Database library.db berhasil diinisialisasi.")


if __name__ == '__main__':
    init_db()