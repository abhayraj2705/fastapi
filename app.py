from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def Home():
    return {"message":"Welcomr FastApi"}

@app.get("/abhayraj")
def Abhayraj():
    return {"message":"Hey my name is abhayraj welcome to the fastapi"}

@app.get("/contact")
def contact():
    return {"messsage":"Hey you can contact us on linked in"}
# get post put patch 
# get is the getting the data from the database 
# post is the posting the data to the database 
# put is the changing the whole databse 
# patch the changing the some part of the databse 
# this is the example for the dynamic url 

@app.get("/users/{user_id}")
def get_user(user_id):
    return {"user_id":user_id}
