import snap7
from snap7.util import *
import sqlite3
import time

# PLC connection parameters
PLC_IP = '192.168.0.2'  # Replace with the PLC's IP address
RACK = 0
SLOT = 1

# Database file path
DB_FILE = "Munjal Test Data.db"

# Connect to PLC
def connect_to_plc():
    client = snap7.client.Client()
    client.connect(PLC_IP, RACK, SLOT)
    return client

# Read data from the PLC
def read_plc_data(client, db_number, start, size):
    data = client.db_read(db_number, start, size)
    return data

# Write data to the PLC
def write_plc_data(client, db_number, start, data):
    client.db_write(db_number, start, data)

# Mark order and station as dispatched and update divert if conditions are met
def check_and_update_order(order_id, station, client, db_number, divert_address):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    
    try:
        # Check if Order_Id exists in the Order table with 'Inactive' status
        cursor.execute("SELECT * FROM 'Order' WHERE Order_Id = ? AND Status = 'InActive'", (order_id,))
        order = cursor.fetchone()
        
        if order:
            # Check if station exists for the given Order_Id
            cursor.execute("SELECT * FROM Order_Details WHERE Order_Id = ? AND station = ?", (order_id, station))
            order_detail = cursor.fetchone()
            
            if order_detail:
                # Update dispatched to True in the database
                cursor.execute("UPDATE Order_Details SET dispatched = 1 WHERE Order_Id = ? AND station = ?", (order_id, station))
                connection.commit()
                print(f"Dispatched set for Order ID {order_id} at station {station}.")

                # Set divert to True in PLC
                divert_data = bytearray([1])  # Setting divert to 1 (True)
                write_plc_data(client, db_number, divert_address, divert_data)
                print(f"Divert set to True for Order ID {order_id} at station {station} in PLC.")
            else:
                print(f"Station {station} not found for Order ID {order_id}.")
        else:
            print(f"Order ID {order_id} not found or not 'Inactive'.")

    except sqlite3.Error as e:
        print("Database error:", e)
    finally:
        connection.close()

# Main function to connect to the PLC and check for orders
def main():
    # DB settings in PLC for Order_Id, station, and divert
    ORDER_ID_ADDRESS = 0  # Start byte for Order_Id
    STATION_ADDRESS = 2  # Start byte for station
    DIVERT_ADDRESS = 4    # Start byte for divert
    DB_NUMBER = 1         # Data block number in TIA Portal

    # Connect to PLC
    client = connect_to_plc()
    if not client.get_connected():
        print("Failed to connect to PLC.")
        return

    try:
        # Continuously check PLC for new data
        while True:
            # Read Order_Id (as integer), station (as integer), and divert (as boolean)
            data = read_plc_data(client, DB_NUMBER, 0, 10)
            order_id = get_int(data, ORDER_ID_ADDRESS)
            station = get_int(data, STATION_ADDRESS)
            divert = get_bool(data, DIVERT_ADDRESS, 1)

            # Check and update the database if conditions are met
            check_and_update_order(order_id, station, client, DB_NUMBER, DIVERT_ADDRESS)

            # Wait a bit before the next check
            time.sleep(1)

    finally:
        client.disconnect()
        client.destroy()

if __name__ == "_main_":
    main()