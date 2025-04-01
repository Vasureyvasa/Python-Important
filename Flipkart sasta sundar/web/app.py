import sqlite3
from flask import Flask, render_template 

conn = sqlite3.connect('Manjul Test Data.db',check_same_thread=False)
app = Flask(__name__) 

@app.route('/')
def index(): 
    # Execute a SQL query to fetch data from the table 
    result = conn.execute('select * from Order_Details')  
    data = result.fetchall() 
    print(data)
    return render_template('index.html', data=data)
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()
    conn.close()  