from flask import Flask, redirect, url_for,session,request,render_template,session,flash
import smtplib
import random
from pymongo import MongoClient

cluster=MongoClient('mongodb+srv://hiring:hysea@cluster0.pxm7e.mongodb.net/hiring?retryWrites=true&w=majority')

db = cluster['Hysea']

profile = db['Profile']

app=Flask(__name__)
app.secret_key = 'abc'
def users(name1,name2,mail,mobile,ver,otp,clg=None,branch=None,languages=None,tech1=None,tech2=None,age=None,grad=None):
    doc = {"name1":name1,"name2":name2,"mail":mail,"mobile":mobile,"ver":ver,"otp":otp,"clg":clg,"branch":branch,"languages":languages,"tech1":tech1,"tech2":tech2,"age":age,"grad":grad}
    x = profile.insert_one(doc)
@app.route('/')
def home():
    print(session)
    return render_template('index.html')

@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method == "POST":
        #print(request.form['sig'])
        session['user'] = request.form['name1']
        session['mail'] = request.form['mail']
        #a = request.form['emaill']
        #f = profile.find_one({'email':session['mail']})
        f = None
        #print(f)
        if f== None:
            num = random.randint(100000,1000000)
            users(name1=request.form['name1'],name2=request.form['name2'],mail=request.form['mail'],mobile = request.form['num'],ver = 'F',otp=num)
            #print(usr.name1,usr.name2,usr.mail)

            # creates SMTP session
            s = smtplib.SMTP('smtp.gmail.com', 587)

            # start TLS for security
            s.starttls()

            # Authentication
            s.login("karthiksurineni2@gmail.com", "ikol@12@goe")

            # message to be sent
            message = "Your OTP is " + str(num)
            SUBJECT = "no-reply"
            message = 'Subject: {}\n\n{}'.format(SUBJECT, message)
            # sending the mail
            s.sendmail("karthiksurineni2@gmail.com", session['mail'], message)

            # terminating the session
            s.quit()

            return redirect(url_for('auth'))
        else:
            #print(f.name1,f.name2,f.mail)
            flash('This email id is already registered')
        render_template('index.html')

    return render_template('index.html')
@app.route('/auth',methods=['GET','POST'])
def auth():
    if request.method == 'POST':
        tempotp = request.form['otp']
        pas1 = request.form['pas1']
        pas2 = request.form['pas2']
        if pas1 == pas2:
            f = profile.find_one({"mail":session['mail']})
            #print(tempotp == f['otp'])
            if f['otp'] == int(tempotp):
                profile.update_one({"mail":session['mail']},{"$set":{"password":pas1,"ver":'T'}})

                return 'Verified'
            else:
                flash('Enter Valid OTP')
                return render_template('auth.html',mail = session['mail'])
        else:
            flash('Enter same password')
            return render_template('auth.html',mail = session['mail'])
    return render_template('auth.html',mail = session['mail'])

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        #print(request.form['sig'])
        #session['user'] = request.form['name1']
        a = request.form['emaill']
        session['mail'] = a
        #print(a)
        f = profile.find_one({"mail":a})
        #print(f)
        if f == None:
            flash("Invalid Usermail")
            return render_template('index.html')
        else:
            if f["password"] == request.form['pas']:
                session['user'] = f["name1"]
                session['password'] = f["password"]
                return render_template('order.html')
        flash('Invalid Password')
        render_template('index.html')

    return render_template('index.html')
#
# @app.route('/order',methods=['GET','POST'])
# def order():
#     if request.method == 'POST':
#         fo = food(item = 'Biryani',user = session['mail'],date = (str(x.day)+'-'+str(x.month)+'-'+str(x.year)),price = 100)
#         db.session.add(fo)
#         db.session.commit()
#         f = food.query.filter_by(price = 100).all()
#         return render_template('order.html',co=fo.price,f=f)
#     return render_template('order.html')
if __name__ == '__main__':
    app.run(debug=True)
