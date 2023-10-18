from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import smtplib
import requests
from pathlib import Path

UPLOAD_DIR = Path()/ "uploads"


from fastapi.staticfiles import StaticFiles

from utils.azure_sql_database import *
from utils.jiraAPIWrapper import *
from utils.jira_info import *
from utils.credentials import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/imgs", StaticFiles(directory="imgs"), name='movies_pix.jpg')


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_response(request: Request,
                            username: str = Form(...),
                            password: str = Form(...),
                            ):

    try:
        read_from_table(username,password)

    except:
        return "User Does Not Exist"

    return

@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_response(request: Request,
                            lastname: str = Form(...),
                            firstname: str = Form(...),
                            email: str = Form(...),
                            username: str = Form(...),
                            dob = Form(...),
                            gender: str = Form(...),
                            psw: str = Form(...), psw_repeat: str = Form(...)
                            ):

    try:
        insert_into_table(lastname, firstname, email, username, dob, gender)

    except:
        return "User Already Exist"

    return


@app.get("/forgot_password", response_class=HTMLResponse)
def forgot_password(request:Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@app.post("/forgot_password")
async def password(request: Request, email: str = Form(...),
                   username: str = Form(...)):
    print(username, email)

    sender_email = "n4naynay@gmail.com"
    receiver_email = email
    subject = (" SUBJECT: Forgot Password to Movies Point")
    message = (
        " In response to your forgot password request, kindly click on this link for a password reset. Do ignore this email if you are not the requestor")
    text = f"subject : {subject} \n\n {message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, text)

    print("Email has been sent to " + receiver_email)


    #return read_from_table(username)
    #return "If your email is registered with us, a reset password email will be sent to you"


@app.get("/contact_us", response_class=HTMLResponse)
async def contact_us(request: Request):

    return templates.TemplateResponse("contact_us.html", {"request": request})


@app.post("/contact_us")
async def contact_us(request: Request, firstname: str = Form(...),
                     lastname: str = Form(...),
                     email: str = Form(...),
                     phone: str = Form(...),
                     summary: str = Form(...),
                     detail: str = Form(...),
                     username: str = Form(...),
                     file: UploadFile = Form(...)):
    #print(firstname, lastname, detail, phone, email,file)  ### Create JIRA ticket logging
    #print (dir(file))

    data = await file.read()
    save_to = UPLOAD_DIR / file.filename
    with open(save_to, "wb") as f:
        f.write(data)
    return {"filename" : file.filename}
    #file.write("testing")
    from utils.jira_info import fields
    fields["project"]["key"] = "MOVIES"
    fields["issuetype"]["name"] = "Task"
    fields["customfield_10043"] = email
    fields["customfield_10040"] = phone
    fields["summary"] = summary
    fields["description"] = detail
    fields["customfield_10034"] = [f"{firstname}-{lastname}"]
    fields["customfield_10041"] = username

    print(fields)

    moviejira = JiraAPI.create_conn()
    moviejira.create_issue(fields)
