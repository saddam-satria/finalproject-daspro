from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from util import util
from controllers import Users,Booking
import sys
import re 
import os

class MainWidget(QtWidgets.QStackedWidget):
    def __init__(self):
        super(MainWidget, self).__init__() 
        self.addWidget(WelcomeScreen())
        self.setWindowTitle("Salon")
        self.setFixedHeight(780)
        self.setFixedWidth(1080)  
        

class WelcomeScreen(QtWidgets.QMainWindow):
    def __init__ (self): 
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcome.ui",self)
       
        self.btn_login.clicked.connect(self.loadUiLogin)
        self.btn_register.clicked.connect(self.loadUiRegister)
    
    def loadUiLogin(self):
        widget.addWidget(LoginScreen())
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def loadUiRegister(self):
        widget.addWidget(RegisterScreen())
        widget.setCurrentIndex(widget.currentIndex() + 1)
             
class BookingScreen(QtWidgets.QMainWindow):
    def __init__(self,email,nama,username):
        super(BookingScreen,self).__init__()
        loadUi('ui/booking.ui',self)
        self.nama = nama
        self.email = email
        self.username = username
        self.input_nama.setText(self.nama)
        self.input_email.setText(self.email)

        self.btn_cek_kode.clicked.connect(self.goToCekKode)
        self.btn_book.clicked.connect(self.booknow)
        
    def goToCekKode (self):
        widget.addWidget(CekKode(self.nama,self.email,self.username))
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def booknow(self):
        nama = self.input_nama.text()
        email = self.input_email.text()
        nohp = self.input_nohp.text()
        jadwal = self.jadwal.text()
        # pilihan paket di input
        paket = self.list_price_list.currentItem()
        choice = ""

        if(paket != None):
            choice = paket.text()
        else:
            paket = ""
        

        if len(nama) < 1 or len(email) < 1 or len(nohp) < 1 or len(jadwal) < 1 or len(choice) < 1:
            self.hasil.setText("Data tidak boleh kosong")
            self.hasil.setStyleSheet('font-weight: 500;font-size: 18px;color: red;')
        else:
            if(re.search(r"^[0-9]{11,12}$" ,nohp) == None):
                self.hasil.setText("No hp harus valid")
                self.hasil.setStyleSheet('font-weight: 500;font-size: 18px;color: red;')
            else: 
                if(re.search(r"^([a-z0-9]+)@{1}([a-z]+)([\.]{1})([a-z]{2,4})\.?([a-z]{2,4})?$",email) == None):
                    self.hasil.setText("Email harus benar")
                    self.hasil.setStyleSheet('font-weight: 500;font-size: 18px;color: red;')
                else:
                    booking = Booking ()
                    kodeBooking = booking.kodeBooking()
                    booking.booknow(nama,email,nohp,jadwal,kodeBooking,self.username,choice)
                    self.hasil.setTextInteractionFlags(Qt.TextSelectableByMouse)   
                    self.hasil.setText(f"simpan kode berikut {kodeBooking}") 
                    self.hasil.setStyleSheet('font-weight: 500;font-size: 18px;color: green;')

class CekKode(QtWidgets.QMainWindow):
    def __init__(self,nama,email,username):
        super(CekKode,self).__init__()
        loadUi("ui/cek_kode.ui",self)
        self.nama = nama 
        self.email = email
        self.username = username
        self.btn_back.clicked.connect(self.back)
        self.btn_cek.clicked.connect(self.cek)
    def back(self):
        widget.addWidget(BookingScreen(self.email,self.nama,self.username))
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def cek(self):
        kode = self.kode_book.text()
        booking = Booking()
        result = booking.cekKode(kode,self.username)
        if result['error'] == True:
            self.hasil.setText(result['msg'])
            self.hasil.setStyleSheet("font-weight: 500;font-size: 18px;color: red;")
        else:
            self.hasil.setText(result['msg'])
            self.hasil.setStyleSheet("font-weight: 500;font-size: 18px;color: green;")
            self.hasil_email.setText(result['email'])
            self.hasil_tanggal.setText(result['jadwal'])

            self.hasil_harga.setText(f"Total harga: {str(result['harga'])}")


class LoginScreen(QtWidgets.QMainWindow): 
    def __init__ (self): 
        super(LoginScreen, self).__init__()
        loadUi("ui/login.ui",self)
        self.btn_login.clicked.connect(self.validation)
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.btn_register.clicked.connect(self.backToRegister)
        self.btn_lupa_password.clicked.connect(self.lupaPasswordScreen)

    def backToRegister(self):
        widget.addWidget(RegisterScreen())
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def lupaPasswordScreen(self):
        widget.addWidget(LupaPasswordScreen())
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def validation(self): 
        username = self.input_username.text()
        password = self.input_password.text()
        if(len(username) < 1 or len(password) < 1):
            self.label_error.setText("Email atau password harus diisi")
            self.label_error.setStyleSheet("color: red; font-size: 18px")
        else:
            self.login(username,password)

    def login(self,username,password): 
        # Firebase connect / DB connect
        user = Users()
        result = user.login(username,password)



        if result['error'] == True:
            self.label_error.setText(result["msg"])
            self.setStyleSheet("color: red;  font-size: 18px")
        else:
            self.label_error.setText(result["msg"])
            self.setStyleSheet("color: green;  font-size: 18px")
            self.bookingpage(result['user'])        

        self.input_username.setText("")
        self.input_password.setText("")
    def bookingpage(self,user):
        email = user['email']
        nama = user['nickname'] + " " +  user['lastname'] 
        username = user['username']
        widget.addWidget(BookingScreen(email,nama,username))
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
        

class RegisterScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(RegisterScreen,self).__init__()
        loadUi("ui/register.ui",self)
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.btn_login.clicked.connect(self.backToLogin)
        self.btn_register.clicked.connect(self.validation)
    def backToLogin(self):
        widget.addWidget(LoginScreen())
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def validation(self):
        nickname = self.input_nickname.text() 
        lastname = self.input_lastname.text() 
        email = self.input_email.text()
        username = self.input_username.text() 
        password = self.input_password.text() 
        print(self.list_price_list)

        validate = { 
            "username": r"^[a-z0-9]+$",
            "password": r"^([A-Z]+)([\w\d\s.]+)$",
            "email" : r"^([a-z0-9]+)@{1}([a-z]+)([\.]{1})([a-z]{2,4})\.?([a-z]{2,4})?$"
        }
        if(len(nickname) < 1 or len(email) < 1 or len(lastname) < 1 or len(password) < 1):
            self.label_error.setText("Kolom tidak boleh kosong")
            self.label_error.setStyleSheet("color: red ; font-size: 18px")
        else:
            # Email 
            if re.search(validate["email"], email) == None:
                self.label_error.setText("Format email harus benar & menggunakan @")
                self.label_error.setStyleSheet("color: red ; font-size: 18px")
            else: 
                # username
                if re.search(validate["username"], username) == None: 
                    self.label_error.setText("Username harus huruf kecil tanpa spasi")
                    self.label_error.setStyleSheet("color: red;  font-size: 18px" )
                else: 
                    # password harus lebih dari 8 karakter 
                    if(len(password) > 7): 
                        if re.search(validate["password"], password) == None: 
                            self.label_error.setText("Password harus huruf besar di awal")
                            self.label_error.setStyleSheet("color: red;  font-size: 18px")
                        else: 
                            # Validation Success
                            self.register(nickname,lastname,email,username,password)
                    # password huruf besar
                    else:
                        self.label_error.setText("Password harus memiliki 8 karakter")
                        self.label_error.setStyleSheet("color: red;  font-size: 18px")
        

    def register(self,nickname,lastname,email,username,password): 
        users = Users()
        user = users.register(nickname,lastname,email,username,password)
        if user != None: 
            if user["msg"]["email"]:
                self.label_error.setText(user["msg"]["email"])
                self.label_error.setStyleSheet("color: red; font-size: 18px")
            else: 
                if user["msg"]["username"]:
                    self.label_error.setText(user["msg"]["username"])
                    self.label_error.setStyleSheet("color: red; font-size: 18px")
        else:
            self.label_error.setText("Sukses registrasi")
            self.label_error.setStyleSheet("color: green; font-size: 18px")

        self.input_nickname.setText("") 
        self.input_lastname.setText("") 
        self.input_email.setText("") 
        self.input_username.setText("") 
        self.input_password.setText("") 
            

class LupaPasswordScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(LupaPasswordScreen, self).__init__()
        loadUi('ui/lupa_password.ui',self)
        self.btn_password.clicked.connect(self.getPassword)
        self.btn_back_to.clicked.connect(self.backToLoginScreen)
    def backToLoginScreen(self):
        widget.addWidget(LoginScreen())
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def getPassword(self):
        user = Users()
        username = self.input_username.text()
        password = user.lupapassword(username)
        self.password.setText(password["msg"])
        self.password.setStyleSheet(f"font-size: 16px; color: { 'red' if password['error'] == True else 'green' }")

# App 

app =QtWidgets.QApplication(sys.argv)
widget = MainWidget()
widget.show()
# widget.setWindowFlags(QtCore.Qt.FramelessWindowHint)
# widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)


try:
    sys.exit(app.exec_())
except: 
    print("Keluar dari aplikasi")
