from flask import Flask, redirect, url_for,session,request,render_template,session,flash
import smtplib
import random
from pymongo import MongoClient
import datetime
cluster=MongoClient('mongodb+srv://hiring:hysea@cluster0.pxm7e.mongodb.net/hiring?retryWrites=true&w=majority')
from twilio.rest import Client

account_sid = 'ACf557040cefaf4ecf1d99fa7f73f54261'
auth_token = 'f15ba2016580bae84794645d8282e3ef'
client = Client(account_sid, auth_token)
db = cluster['Hysea']

profile = db['Profile']
jobs = db['jobs']
applications = db['applications']
def clean(number):
    number = str(number)
    if len(number)==13:
        return number
    if len(number) == 10:
        return ('+91'+str(number))
app=Flask(__name__)
app.secret_key = 'abc'
def users(name1,name2,mail,mobile,ver,otp,type,clg=None,branch=None,languages=None,tech1=None,tech2=None,age=None,grad=None,password=None):
    doc = {"name1":name1,"name2":name2,"mail":mail,"mobile":mobile,"ver":ver,"otp":otp,"type":type,"clg":clg,"branch":branch,"languages":languages,"tech1":tech1,"tech2":tech2,"age":age,"grad":grad,"password":password}
    x = profile.insert_one(doc)
@app.route('/')
def home():
    a = list(jobs.find())
    #print(a)
    print(session)
    if 'user' in session:
        if session['type'] == 'org':
            return render_template('home.html',a = a,app=True)
        return render_template('home.html',a = a,cre = True)
    else:
        return render_template('home.html',a=a)

@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method == "POST":
        #print(request.form['sig'])
        session['user'] = request.form['name1']
        session['mail'] = request.form['mail']
        option = request.form['options']

        #a = request.form['emaill']
        #f = profile.find_one({'email':session['mail']})
        f = None
        #print(f)
        if f== None:
            num = random.randint(100000,1000000)
            users(name1=request.form['name1'],name2=request.form['name2'],type = option,mail=request.form['mail'],mobile = request.form['num'],ver = 'F',otp=num)
            message = "Your OTP is " + str(num)
            num1 = clean(request.form['num'])
            message = client.messages \
                             .create(
                                  body= message,
                                  from_='+13342588630',
                                 to=num1
                              )
            print(message.sid)

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
                flash("Your Mobile Number has been verified")
                return redirect(url_for('login'))
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
        #session['type'] = 'org'
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
                session['type'] = f['type']
                return redirect(url_for('update'))
        flash('Invalid Password')
        render_template('index.html')

    return render_template('index.html')
@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        a = {"clg":request.form['clg'],"branch":request.form['branch'],"languages":request.form['languages'],"tech1":request.form['tech1'],"tech2":request.form['tech2'],"age":request.form['age'],"grad":request.form['grad']}
        profile.update_one({"mail":session['mail']},{"$set":a})
        flash('Details Updated successfully')
        return redirect(url_for('update'))
    else:
        return render_template('profile.html',a= profile.find_one({"mail":session['mail']}),b = session['type'])
@app.route('/create',methods=['GET','POST'])
def create():
    if request.method == 'POST':
        li = list(jobs.find({"mail":session['mail']}))
        a = {"_id": (session['mail']+str(len(li))),"name":request.form["name"],"place":request.form["place"],"exp":request.form["exp"],"desc":request.form["desc"],"skill":request.form["skill"],"date":request.form["date"],"span":request.form["span"],"sdate":request.form["sdate"],"mail":session['mail']}
        flash('Created successfully')
        x = jobs.insert_one(a);
        return redirect(url_for('create'))
    else:
        return render_template('create.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
@app.route('/<name>',methods=['GET','POST'])
def apply(name):
    f = jobs.find_one({"_id":name})
    #print(list(f),'hello')
    if f ==None:
        f = profile.find_one({'mail':name})
        if f !=None:
            return render_template('display.html',f = f)
    else:
        if session['type'] == 'org':
            f = list(applications.find({'job_id':name}))
            if f != None:
                return render_template('userlist.html',appl = f,l = len(f))
        if request.method =='POST':
            x = datetime.datetime.now()
            ap = applications.insert_one({'job_id':name,'applicant':session['user'],'applicant id':session['mail'],'applied_on':(str(x.day)+'-'+str(x.month)+'-'+str(x.year))})
            flash('Application Submitted')
        else:
            f = profile.find_one({'mail':session['mail']})
            return render_template('display.html',f = f,st = True,n = name)
    return redirect(url_for('home'))

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
