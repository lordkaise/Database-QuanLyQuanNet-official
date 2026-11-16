
from database import get_connection

try:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DB_NAME()")
    result = cursor.fetchone()

    print("Ket noi thanh cong!")
    print("Database:", result[0])

    conn.close()

except Exception as e:
    print("Loi ket noi:", e)
