import sqlite3

conn = sqlite3.connect('Manjul Test Data.db')

var1=conn.execute('select * from Order_Details where Order_Id="O1"')  

# for i in var1:
#     print(i[1]) 
  
conn.close()  