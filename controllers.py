import pymongo
import os
from dotenv import load_dotenv
import bcrypt
import datetime
import random
import string

from datetime import date


load_dotenv()

class DB: 
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv("DB_URL"))
        self.db = self.client['salon']
        self.userCollection = self.db["users"]
        self.priceList = {
            "kerembat": 30000,
            "potong rambut": 10000,
            "warnain rambut" : 100000,
            "cukur alis": 5000,
            "rebonding": 200000 
        }
        
       
class Users(DB):
    def __init__(self):
        super(Users,self).__init__()
    def validate(self,username,email):
        msg = {
            "username": "",
            "email": ""
        }
        usernameUser= self.userCollection.find_one({"username": username})
        emailUser = self.userCollection.find_one({"email": email})
        if usernameUser != None: 
            msg["username"] = "Username sudah di gunakan"
        if emailUser != None: 
            msg["email"]= "Email sudah digunakan"

        return {"msg": msg}

    def register(self,nickname,lastname,email,username,password):
        checkUser = self.validate(username,email)
        if checkUser["msg"]["username"] or checkUser["msg"]["email"]:
            return checkUser

        hashPassword = bcrypt.hashpw(str.encode(password),bcrypt.gensalt())
        newUsers = {"nickname" : nickname, "lastname": lastname, "email": email, "username": username, "encryptPassword": hashPassword.decode(),"password": password,"lastActive":datetime.datetime.now() }
        self.userCollection.insert_one(newUsers)   
         
        
    def login(self,username,password):
        # username exists
        query = {"username": username}
        user = self.userCollection.find_one(query)
        self.userCollection.update_one(query, {"$set": {"lastActive": datetime.datetime.now()}})
        if user == None: 
            return {"msg": "Username tidak ditemukan","error" : True}
        
        # Check Password
        passwd = bcrypt.checkpw(str.encode(password), str.encode(user["encryptPassword"]))
        if passwd != True: 
            return {"msg": "Password salah","error" : True}
        else:
            return {"msg": "Sukses login", "user" :  user , "error" : False}
    
    def lupapassword(self,username):
        if len(username)  <  1:  
            return {"error": True, "msg": "Silahkan isi username anda"}
        
        if username == "admin": 
            return {"error": True, "msg": "tidak bisa akses admin"}

        user = self.userCollection.find_one({"username": username})
        if user == None: 
            return {"error": True, "msg": "Username tidak ditemukan"}
        else: 
            
            return { "error": False, "msg": f'Password anda adalah {user["password"]}, silahkan login kembali'}

class Booking(DB):
    def __init__(self):
        super(Booking,self).__init__()

    def booknow(self,nama,email,nohp,jadwal,kode,username,choice):
       
        total = self.priceList[choice]
        
        print(total)
        self.userCollection.update_one({"username" : username}, {
            "$set" : {"dataBooking": {"nama": nama, "email": email, "nohp": nohp ,"jadwal": jadwal,"kodeBooking": kode, "harga": total, "choice": choice}}
        },
        upsert=True
        )
    def kodeBooking(self,size=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    def cekKode(self,kode,username):
        result = self.userCollection.find_one({"username": username})
        if "dataBooking" in result:
            kodeDB = result['dataBooking']['kodeBooking']
            if kode != kodeDB:
                return {"msg": "Kode Booking salah", "error": True}
            return {"msg": "Kode berhasil didapatkan","error" : False, "email": result['email'], "jadwal": result['dataBooking']['jadwal'], "harga": result['dataBooking']['harga'], "Kode_Booking" : result['dataBooking']['kodeBooking']}
        else:
            return {"msg": "Anda belum booking", "error": True}
        

