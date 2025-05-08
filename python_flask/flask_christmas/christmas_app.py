# pip install pymysql
import pymysql
import pandas as pd
from flask import Flask, render_template, request, jsonify, url_for
import datetime
import os

db_config ={
    'host':'13.124.175.208'
   ,'user':'myuser'
   ,'password':'myuser'
   ,'database':'mydb'
}
def get_connection():
    return pymysql.connect(**db_config)

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/get_card', methods=['POST'])
def get_card():
    nm = request.form['nm']
    email = request.form['email']
    if nm != '' and email != '':
        conn = get_connection()
        card = pd.read_sql(sql="""
                SELECT * 
                FROM cards
                WHERE email = %s
                AND   nm = %s
            """, con=conn, params=(email, nm))
        print(card)
        conn.close()
        if not card.empty:
            return render_template('christmas.html'
                , message1=card.iloc[0]['message1']
                , message2=card.iloc[0]['message2']
                , message3=card.iloc[0]['message3']
                , nm=nm, email=email, code=200)
        else:
            return render_template('index.html',code=404)
    else:
        return render_template('index.html', code=404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

