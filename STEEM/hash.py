import sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect("mydatabase.db")
db.row_factory = sqlite3.Row     # <--- THIS FIXES THE ERROR

# --- Admin passwords ---
admins = db.execute("SELECT AdminID, Password FROM Admins").fetchall()
for admin in admins:
    hashed = generate_password_hash(admin["Password"])
    db.execute(
        "UPDATE Admins SET Password=? WHERE AdminID=?",
        (hashed, admin["AdminID"])
    )

# --- Developer passwords ---
devs = db.execute("SELECT DeveloperID, Password FROM Developers").fetchall()
for dev in devs:
    hashed = generate_password_hash(dev["Password"])
    db.execute(
        "UPDATE Developers SET Password=? WHERE DeveloperID=?",
        (hashed, dev["DeveloperID"])
    )

# --- User passwords ---
users = db.execute("SELECT UserID, Password FROM Users").fetchall()
for user in users:
    hashed = generate_password_hash(user["Password"])
    db.execute(
        "UPDATE Users SET Password=? WHERE UserID=?",
        (hashed, user["UserID"])
    )

db.commit()
db.close()
