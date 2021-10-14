from flask import Flask, render_template, request, session, redirect
import mysql.connector as myc
import os

my_db = myc.connect(host='localhost',user='root',passwd='root',database='project1')
my_cursor = my_db.cursor()

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    if 'user_id' not in session:
        return render_template('index.html')
    else:
        return redirect('login')

@app.route('/home')
def loginhome():
    if 'user_id' in session:
        return render_template('index2.html')
    else:
        return redirect('login')

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('login.html')

@app.route('/register')
def signup():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('signup.html')

@app.route('/profile', methods = ['POST','GET'])
def profile():
    global data
    if request.method == 'POST':
        result = request.form
        email = result['Email']
        password = result['Password']
        my_cursor.execute(f"select customer_id,customer_name,email,mobile from customer where email = '{email}' and password = '{password}'")
        data = my_cursor.fetchone()
        my_db.commit()

        if data != None:
            session['user_id'] = data[0]
            return render_template('index2.html', loginmsg = "You Logged in successfully ")
        else:
            failed = 'Email or Password are wrong'
            return render_template('login.html', failed = failed)
    if 'user_id' in session:
        uid = session['user_id']

        my_cursor.execute(f"select customer_id,customer_name,email,mobile from customer where customer_id = {uid}")
        detail = my_cursor.fetchone()
        my_db.commit()
        return render_template('profile.html', detail = detail)

@app.route('/process')
def process():
    select = request.args.get('selection')
    print(str(select))
    return redirect('shopping')
        
@app.route('/profile/newuser', methods = ['POST','GET'])
def newuser():
    
    if request.method == 'POST':
        result = request.form
        name = result['Name']
        password = result['Password']
        email = result['Email']
        mobile = result['Mobile']
        my_cursor.execute(f"select * from customer where email = '{email}'")
        account = my_cursor.fetchone()
        if account:
            return render_template('signup.html', regmsg = 'This Email is already registered, login now')
        else:
            my_cursor.execute(f"insert into customer(customer_name,password,email,mobile) values('{name}','{password}','{email}',{mobile})")
            my_db.commit()

            session['user_id'] = name
            return render_template('index2.html', regmsg = 'You are successfully registered')
        
@app.route('/shopping', methods = ['POST','GET'])
def shopping():
    if 'user_id' in session:
        my_db = myc.connect(host='localhost',user='root',passwd='root',database='project1')
        my_cursor = my_db.cursor()
        if request.method == 'POST':
            item = request.form.get('shop-item')
            my_cursor.execute(f"select product_id,product_name,product_price,unit from product where product_name like '%{item}%'")
            data = my_cursor.fetchmany(5)
            if data != None:
                return render_template('shopping.html', data = data)
            else:
                return redirect('loginhome')
        else:
            my_cursor.execute(f"select product_id,product_name,product_price,unit from product order by product_price desc")
            data = my_cursor.fetchmany(5)

            if data != None:
                return render_template('shopping.html', data = data)
            else:
                return redirect('loginhome')

    else:
        return render_template('index.html', alertmsg = "Login/Register First for shopping")

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('login')


if __name__ == "__main__":
    app.run(debug = False)