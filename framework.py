import os

from flask import Flask, redirect, render_template, request, session, url_for
import pyrebase

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.realpath(__file__))

app.secret_key = os.urandom(24)
config = {
  
  "apiKey": "AIzaSyAYCLjj_XCZMrfwgk-0RxViXbQmskAOXvs",
  "authDomain": "flaskwebapp-23578.firebaseapp.com",
  "databaseURL": "https://flaskwebapp-23578.firebaseio.com",
  "projectId": "flaskwebapp-23578",
  "storageBucket": "flaskwebapp-23578.appspot.com",
  "messagingSenderId": "551767331469",
  "appId": "1:551767331469:web:f3b1ab98ff6ccf4bd908c4",
  "measurementId": "G-6KNB3S3SMC",
  "serviceAccount": "flaskwebapp-23578-firebase-adminsdk-e6fby-e47ef74135.json"
  
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
user = auth.sign_in_with_email_and_password('chaudashubham@gmail.com','password')

db = firebase.database()
storage = firebase.storage()

ALLOWED_EXTENSIONS = ['pdf','doc','png','jpg','jpeg']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods = ["GET"])
def index():
    if session.get("userName"):
        return render_template("home.html")
    return redirect(url_for("signin"))

@app.route("/signin", methods = ["GET", "POST"])
def signin():
    if session.get("userName"):
        return redirect(url_for("index"))
    if request.method == "POST":
        enrollNo = request.form.get("enrollNo")
        password = request.form.get("password")
        if enrollNo == "admin" and password == "admin":
            session["adminCh"] = True
            return redirect(url_for("admin"))
        chlogin = db.child("users").child(enrollNo).get()
        if chlogin.val() == None:
            return render_template("signin.html", error = "Invalid Login")
        print (type(chlogin.val()["password"]))
        print (password)
        if chlogin.val()["password"] == str(password):
            session["userName"] = enrollNo
            return redirect("/")
        return render_template("signin.html", error = "Invalid Login")
    return render_template("signin.html", error = "")

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if session.get("userName"):
        return redirect(url_for("index"))
    if request.method == "POST":
        data     = {
            "enrollNo" : request.form.get("enrollNo"),
            "email"    : request.form.get("email"),
            "name"     : request.form.get("name"),
            "dept"     : request.form.get("dept"),
            "password" : request.form.get("password")
        }
        chuser = db.child("users").child(data["enrollNo"]).get()
        if chuser.val() == None:
            db.child("users").child(data["enrollNo"]).set(data)
            return redirect(url_for("signin"))
        return render_template("signup.html", error = "Enrollment Number already exists")
    return render_template("signup.html", error = "")

@app.route("/admin", methods = ["GET", "POST"])
def admin():
    if not session.get("userName") or not session["adminCh"]:
        return redirect(url_for("index"))
    pass

@app.route("/dept/<college>/<course>/<int:semester>")
def selection(college, course, semester):
    if not session.get("userName"):
        return redirect(url_for("index"))
    return render_template("selection.html", college = college, course = course, semester = semester)

@app.route("/dept/<college>")
def dept(college):
    if not session.get("userName"):
        return redirect(url_for("index"))
    cl = {
        "iips":"iips.html",
        "ims":"ims.html",
        "scsit":"scsit.html",
        "iet":"iet.html",
        "emrc":"emrc.html",
        "sjmc":"sjmc.html"
    }
    return render_template(cl[college])

@app.route("/dept/<college>/<course>/<int:semester>/upload", methods = ["GET", "POST"])
def upload(college, course, semester):
    if not session.get("userName"):
        return redirect(url_for("index"))
    if request.method == "POST":
        target = os.path.join(APP_ROOT, "")
        if not os.path.isdir(APP_ROOT):
            os.mkdir(target)
        file = request.files["upload"]
        file.save(os.path.join(target, file.filename))
        uploadLoc = college+"/"+course+"/"+str(semester)+"/"+file.filename
        storage.child(uploadLoc).put(file.filename)
        os.remove(os.path.join(target, file.filename))
        db.child("uploads").child(session.get("userName")).set(uploadLoc)
        return redirect("/")
    return render_template("upload.html")

@app.route("/dept/<college>/<course>/<int:semester>/view", methods = ["GET", "POST"])
def view(college, course, semester):
    if not session.get("userName"):
        return redirect(url_for("index"))
    if request.method == "POST":
        val = request.form.get("download")
        return("<a href = "+storage.child(college+'/'+course+'/'+str(semester)+'/'+val).get_url(val)+">Click here</a><br><a href = '/'>Home</a>")
    result = db.child("uploads").get()
    link = college+"/"+course+"/"+str(semester)
    returnDict = {}
    for data in result.each():
        if link in data.val():
            val = data.val().lstrip(college+"/"+course+"/"+str(semester)+"/")
            returnDict[data.key()] = val
    print(returnDict)
    return render_template("view.html", returnDict = returnDict)

@app.route("/logout")
def logout():
    if not session.get("userName"):
        return redirect(url_for("index"))
    session.pop("userName")
    session["adminCh"] = False
    return redirect("signin")
