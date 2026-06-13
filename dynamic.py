from fastapi import FastAPI

app=FastAPI()




@app.get("/users/{user_id}")
def get_user(user_id:int):
    return {"user_id":user_id}

@app.get("/users")
def name(name:str=None):
    return {"name":name}


# this is the example for the default parameters 

@app.get("/items")
def get_items(name:str=None , price:int=0):
    return {
        "name":name,
         "price":price
    }

# this is the example for the post request 

@app.post("/create_user")
def create_user(name:str,age:int,college:str,semester:int):
    return {

        "message":"the user is created successfully",
        "data":{
            "name":name,
            "age":age,
            "college":college,
            "semester":semester
        }
    }
