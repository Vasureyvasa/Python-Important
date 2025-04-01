import sqlite3
DB_FILE = "Manjul Test Data.db"
order_id = "O1" 
station = 6
divert = 0     
dataRecord = {
    "PLC": "Simulated PLC",  
    "table": []
}

def check_and_update_order(order_id, station):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM Order_Details WHERE Order_Id = ? AND station = ?", (order_id, station))
        order_detail = cursor.fetchone()
        if order_detail:
            cursor.execute("UPDATE Order_Details SET dispatched = 0 WHERE Order_Id = ? AND station = ?", (order_id, station))
            cursor.execute("UPDATE 'Order' SET Status = 'InActive' WHERE Order_Id = ?", (order_id,))
            connection.commit()
            divert_data = 0
            print("Divert set to:", divert_data)  
            
            return True
    finally:
        connection.close()
i = 1
while i < 2:
    try:
        dataRecord["table"].append({
            "order_id": order_id,
            "stn_id": station,
        })
        updated = check_and_update_order(order_id, station)
        
        if updated:
            print("Data updated successfully.")
        else:
            print("No update needed.")
        
        print(dataRecord)
        i += 1
        
    except KeyboardInterrupt:
        break

print("completed.")