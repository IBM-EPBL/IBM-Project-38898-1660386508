from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify

import numpy as np
import pickle

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

import sqlite3

app=Flask(__name__)
app.secret_key="#@universityflaskapp@#"

# email verification

app.config.from_pyfile('config.cfg')

mail=Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY']) 

# database creation
con=sqlite3.connect("database.db")
print("Opened database successfully")
con.execute("create table if not exists customer(pid integer primary key, name text, email text, password text,status BOOLEAN)")
print("Table created successfully")
con.close()


@app.route('/',methods=['POST','GET'])
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/university')
def university():
    return render_template("university.html")

@app.route('/visual')
def visual():
    return render_template("visual.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/form')
def form():
    return render_template("form.html")

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')
    

# login and rigester


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            name=request.form['name']
            email=request.form['email']
            password=request.form['password']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("INSERT INTO customer(name,email,password) VALUES (?,?,?)",(name,email,password))
            con.commit()
            flash("Registered successfully","success")
        except:
            con.rollback()  
            flash("Problem in Registration, Please try again","danger")
        finally:
            return redirect(url_for("index"))
            con.close()
    else:
        return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("SELECT * FROM customer where email=? and password=?",(email,password))
        data=cur.fetchone()

        if data:
            session["email"]=data["email"]
            print("sent to home")
            return redirect(url_for("home"))
                      
        else:
            flash("Username or Password is incorrect","danger")
            print("not sent to home")
            return redirect(url_for("index"))

@app.route('/check',methods=['POST','GET'])
def check():
    email = session["email"]
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT status FROM customer where email=?",[email])
    data=cur.fetchone()
    con.commit()
    print(data)
    if data[0]==1:
        return render_template("form.html")
    else:
        return render_template("verify.html")



@app.route('/verify')
def verify():
    email = session["email"]

    token = s.dumps(email, salt='email-confirm')

    msg=Message('Confirm Email', sender='ibmproject2023@gmail.com', recipients=[email])

    link=url_for('confirm_email', token=token, _external=True)

    msg.body= 'Please click the link to verify your account to continue  : {} '.format(link)

    mail.send(msg)
    return redirect(url_for("home"))

@app.route('/confirm_email/<token>')
def confirm_email(token):
  try:
    email=s.loads(token, salt='email-confirm' , max_age=3600*5)
  except SignatureExpired:
    return render_template("verify.html")
  con=sqlite3.connect("database.db")
  con.row_factory=sqlite3.Row
  cur=con.cursor()
  cur.execute("UPDATE customer SET status = 1 WHERE email = ?",(email,))
  con.commit()
  con.close()
  return redirect(url_for("form"))

# machine learning model

model = pickle.load(open("uaep_model.pkl","rb"))

@app.route("/predict", methods = ['POST'])
def predict():

    gre  = request.form.get("gre")
    toefl  = request.form.get("toefl")
    ur  = request.form.get("ur")
    sop  = request.form.get("sop")
    lor  = request.form.get("lor")
    cgpa  = request.form.get("cgpa")
    research  = request.form.get("research")

    features = np.array([[gre, toefl, ur, sop, lor, cgpa, research]])

    print(features)

    predictions = model.predict(features)

    print(predictions)

    if predictions[0] >= 0.50:
        print(predictions[0])
        return render_template('result1.html', peredictions=predictions[0]*100)
    else:
        print(predictions[0])
        return render_template('result2.html', peredictions=predictions[0]*100)


if __name__ =='__main__':
    app.run(Debug=True)