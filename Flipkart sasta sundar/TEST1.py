import snap7
from snap7.util import get_string, get_int, get_bool
import keyboard
import time
import sqlite3

# Database and PLC configuration
DB_FILE = "Manjul Test Data.db"
PLC_IP = '192.168.0.2'
PLC_DB_NUMBER = 1  # PLC DB number
STN_ID_SIZE = 4    # Size for reading station ID
DIVERT_BYTE_ADDR = 258  # Address for divert byte
DIVERT_BIT_POSITION = 1  # Bit position for divert
DIVERT_DURATION = 10  # Divert active duration in seconds

# Initialize database and PLC client
plc = snap7.client.Client()
plc.connect(PLC_IP, 0, 1)
conn = sqlite3.connect(DB_FILE)

dataRecord = {
    "PLC": "Simulated PLC",
    "table": []
}

# Dictionary to track stations for each order_id
order_stations = {}
current_order_id = None

def initialize_order(order_id):
    global order_stations, current_order_id
    current_order_id = order_id
    order_stations = {"stations": [], "dispatched": set(), "status": "Under Process"}

    # Retrieve all stations for this order_id from the database
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT DISTINCT station FROM Order_Details WHERE Order_Id = ?", (order_id,))
        stations = cursor.fetchall()
        order_stations["stations"] = [station[0] for station in stations]
    finally:
        connection.close()
    
    print(f"Order {order_id} initialized with stations: {order_stations['stations']}")

def check_and_update_order(order_id, station):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    try:
        # Check if the station has been dispatched for this order_id
        cursor.execute("SELECT dispatched FROM Order_Details WHERE Order_Id = ? AND station = ?", (order_id, station))
        order_detail = cursor.fetchone()
        
        if order_detail and not order_detail[0]:  # dispatched = 0
            # Update the station as dispatched
            cursor.execute("UPDATE Order_Details SET dispatched = 1 WHERE Order_Id = ? AND station = ?", (order_id, station))
            connection.commit()

            # Add this station to the dispatched set
            order_stations["dispatched"].add(station)
            print(f"Station {station} for Order {order_id} dispatched successfully.")

            # Check if all stations are dispatched
            if set(order_stations["stations"]) == order_stations["dispatched"]:
                order_stations["status"] = "Done"
                cursor.execute("UPDATE 'Order' SET Status = 'Done' WHERE Order_Id = ?", (order_id,))
                connection.commit()
                print(f"Order {order_id} marked as Done.")
            else:
                print(f"Order {order_id} status: {order_stations['status']}")
            
            return True
    finally:
        connection.close()
    
    return False

# Main loop to check PLC status and update order details
while True:
    try:
        # Read order_id, station ID, and divert status from PLC
        readOrder_id = plc.db_read(PLC_DB_NUMBER, 0, 254)
        readstn_id = plc.db_read(PLC_DB_NUMBER, 256, STN_ID_SIZE)
        readdivert = plc.db_read(PLC_DB_NUMBER, DIVERT_BYTE_ADDR, 1)

        # Extract values from PLC read
        order_id = get_string(readOrder_id, 0)
        stn_id = get_int(readstn_id, 0)
        readDivert = get_bool(readdivert, 0, DIVERT_BIT_POSITION)

        # Extract only the actual content length of order_id
        actual_length = readOrder_id[1]
        order_id_content = readOrder_id[2:2 + actual_length].decode('utf-8').strip()

        # Initialize new order if order_id changes
        if order_id_content != current_order_id:
            initialize_order(order_id_content)

        # Check if current station is in the list of stations for the order
        if stn_id in order_stations["stations"]:
            # Activate divert for 10 seconds
            plc.db_write(PLC_DB_NUMBER, DIVERT_BYTE_ADDR, bytearray([1 << DIVERT_BIT_POSITION]))
            print(f"Divert activated for station {stn_id} of order {order_id_content}")

            # Delay to keep the divert active
            time.sleep(DIVERT_DURATION)

            # Reset divert
            plc.db_write(PLC_DB_NUMBER, DIVERT_BYTE_ADDR, bytearray([0]))
            print(f"Divert deactivated after {DIVERT_DURATION} seconds")

            # Log the data record
            dataRecord["table"].append({
                "order_id": order_id_content,
                "stn_id": stn_id,
                "readDivert": readDivert
            })

            # Check and update the order for the current station
            updated = check_and_update_order(order_id_content, stn_id)

            if updated:
                print("Data updated successfully.")
            else:
                print("No update needed.")
            
            print(dataRecord)

        # Break the loop if 'Esc' is pressed
        if keyboard.is_pressed('Esc'):
            break

    except KeyboardInterrupt:
        break

# Disconnect PLC and close database connection
plc.disconnect()
conn.close()
print("Process completed.")