# Module Import
import mariadb
import sys
import time

# Add Data Function
def add_data(cur, time, weight, operation):
    cur.execute("INSERT INTO filament_weight.filament_data (time, weight, operation) VALUES (?, ?, ?)", 
                (time, weight, operation))

# Instantiate Connection
try:
   conn = mariadb.connect(
      host="localhost",
      port=3306,
      user="root",
      password="AfstudeerOcto123?",  # Ensure the password is correct
      autocommit=True)
except mariadb.Error as e:
   print(f"Error connecting to the database: {e}")
   sys.exit(1)

# Instantiate Cursor
cur = conn.cursor()

# Add Data
weight = 245
operation = "printing"
time = time.strftime('%Y-%m-%d %H:%M:%S')  # Get current time in required format

add_data(cur, time, weight, operation)

# Close the connection
conn.close()
