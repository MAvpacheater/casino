import sqlite3

def get_or_create_user(user_obj):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_obj.id,))
    row = cursor.fetchone()

    if row:
        user = dict(zip([d[0] for d in cursor.description], row))
    else:
        cursor.execute("INSERT INTO users (user_id, username, last_daily_bonus, last_hourly_bonus) VALUES (?, ?, 0, 0)", 
                       (user_obj.id, user_obj.username or ""))
        conn.commit()
        user = {
            "user_id": user_obj.id,
            "username": user_obj.username,
            "balance": 100,
            "ref_by": None,
            "last_daily_bonus": 0,
            "last_hourly_bonus": 0,
        }
    conn.close()
    return user

def update_balance(user_id, amount):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def set_referral(user_id, ref_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ref_by FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row and row[0] is None and user_id != ref_id:
        cursor.execute("UPDATE users SET ref_by=? WHERE user_id=?", (ref_id, user_id))
        cursor.execute("UPDATE users SET balance = balance + 50 WHERE user_id=?", (ref_id,))
    conn.commit()
    conn.close()

def transfer_coins(from_id, to_username, amount):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (from_id,))
    sender = cursor.fetchone()
    if not sender or sender[0] < amount:
        return "Недостатньо коінів."

    cursor.execute("SELECT user_id FROM users WHERE username=?", (to_username,))
    receiver = cursor.fetchone()
    if not receiver:
        return "Користувача не знайдено."

    to_id = receiver[0]
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, from_id))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, to_id))
    conn.commit()
    conn.close()
    return f"Успішно передано {amount} коінів користувачу @{to_username}."
