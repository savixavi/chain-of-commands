import sqlite3
import os

def init_db():
    if os.path.exists('hr_portal.db'):
        os.remove('hr_portal.db')
        
    conn = sqlite3.connect('hr_portal.db')
    c = conn.cursor()
    
    # NEW: Users table for login/reg
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
    
    # Employees and Secrets (Same as before)
    c.execute('CREATE TABLE employees (id INTEGER, name TEXT, position TEXT, salary TEXT)')
    c.execute('CREATE TABLE secrets (id INTEGER, flag TEXT)')
    
    c.executemany('INSERT INTO employees VALUES (?,?,?,?)', [
        (1, 'Alice', 'Manager', '$90,000'),
        (2, 'Bob', 'Developer', '$75,000')
    ])
    c.execute("INSERT INTO secrets VALUES (1, 'xorion{LLM_Pr0mpt_2_SQLi_Ch4in}')")
    
    conn.commit()
    conn.close()
    print("[+] Database Reset: Users table added.")

if __name__ == "__main__":
    init_db()
