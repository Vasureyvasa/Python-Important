import sqlite3

# Connect to the db
with sqlite3.connect('Manjul Test Data.db') as conn:
	cursor = conn.cursor()

	# Create customers table
	cursor.execute('''
select * from "main"."Order_Details" where Order_Id="O1"
	''')
	conn.commit()
	print("Customers table created successfully.")
	cursor.close()