import snap7
from snap7.util import *
import keyboard
import time

import sqlite3

conn = sqlite3.connect('Manjul Test Data.db')


plc = snap7.client.Client()
db_number = 1  
start_address = 0
size = 4  
table = []

# Connect to PLC
plc.connect('192.168.0.2', 0, 1)

# Reading PLC details
readPLC = plc.db_read(db_number, 22, 254)
PLC = get_string(readPLC, 0)
# var1=conn.execute('select * from Order_Details where Order_Id="O1"')  
# stns=[]
order_id_p=""
i =1
while True:
    try:
        # Read various tags from PLC
        readOrder_id = plc.db_read(db_number, 0, 254)
        readstn_id = plc.db_read(db_number, 256, size)
        readdivert = plc.db_read(db_number, 258, 1)  


        # Extract values from PLC read
        order_id = get_string(readOrder_id, 0)  
        stn_id = get_int(readstn_id, 0) 
        readDivert = get_bool(readdivert, 0, 1)  

        actual_length = readOrder_id[1]


        order_id_content = readOrder_id[2:2 + actual_length].decode('utf-8').strip()
        
    # Convert the byte data to string

        if order_id_content!=order_id_p:
              order_id=order_id_p
              var1=conn.execute('select * from Order_Details where Order_Id=?',(order_id_content,)) 
              stns=[] 
              for i in var1:
                  stns.append(i[1])
        if stn_id in stns:
            plc.db_write(db_number, 258, bytearray([1<<1]))
            
            time.sleep(10)
            plc.db_write(db_number, 258, bytearray([0]))

        dataRecord={
            "order_id": order_id,
            "stn_id": stn_id,
            "readDivert": readDivert
        }
        print(stns)

        if keyboard.is_pressed('Esc'):
            break
    except KeyboardInterrupt:
        break


plc.disconnect()