from datetime import datetime
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QFileDialog
import sys, os
from erros import lista_erros
from siglas import lista_siglas
import images
from winsound import Beep
from time import sleep
import sqlite3

resumo = {}
motorcycles_list = [1]
bank = sqlite3.connect('Harley.db')
cursor = bank.cursor()


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()        
        uic.loadUi('window.ui', self) 
        self.about = about()
        self.EditMotorcycles = EditMotorcycles()
        
       
        self.submit_code.clicked.connect(self.show_line1) 
        self.submit_code.clicked.connect(self.resumao)
        self.save_log.clicked.connect(self.save_txt)
        
        
        self.edit_motorcycles_button.clicked.connect(self.EditMotorcycles.show)
        self.edit_motorcycles_button.clicked.connect(self.EditMotorcycles.update)
        self.about_btn.clicked.connect(self.about.show)
        self.about_btn.clicked.connect(self.bipe)
        
        self.comboBox.currentIndexChanged.connect(lambda x: self.log_area.clear())

        self.code_input.setStyleSheet('background-color: rgb(50,50,50); border-radius:10px; color: rgb(201,52,19); font-size:24px; font-weight: bold; text-align: center')

    
    def show_line1(self):        
        cod = str(self.code_input.text()).strip().upper()
        self.code_input.clear()
        self.system_output.clear()
        
        if cod in lista_erros:            
                self.error_output.setText(f'\nERROR CODE {cod}\n {lista_erros[cod]}\n')
                Beep(900,200)
                resumo.update({cod: lista_erros[cod]})              
        else:
            Beep(400,400)

        try:
                for a in lista_siglas:
                        if a in lista_erros[cod]:
                                self.system_output.setText(f'{lista_siglas[a]}')
                        
        except KeyError:
                self.error_output.setText(f'Error code {cod} not found.')
        
       
    def resumao(self):
        self.log_area.clear()
        date = datetime.today().strftime('%d-%d-%Y')
        self.log_area.addItem(f'DATE:  {date}')
        self.log_area.addItem(f'ERROR CODE            DESCRIPTION            {self.comboBox.currentText()}')
        self.log_area.addItem('¨' * 83)
        for k, v in resumo.items():
                date = datetime.today().strftime('%d-%d-%Y')
                self.log_area.addItem(f'{k}                       {v}')

    def save_txt(self):
        file = str(QFileDialog.getExistingDirectory(self, "Choose where to save the log"))  
        if not os.path.exists(file+f'/{self.comboBox.currentText().upper()}'):             
            os.mkdir(file+f'/{self.comboBox.currentText().upper()}') 
        date = datetime.today().strftime('%d-%d-%Y')
        now = datetime.now().strftime('%H-%M-%S')
        list_widget = self.log_area
        entries = '\n'.join(list_widget.item(ii).text() for ii in range(list_widget.count()))
        with open(f'{file}/{self.comboBox.currentText().upper()}/{date} {now}.txt', 'w') as lista:
            lista.write(entries)
        
    def bipe(self):
        Beep(100,300)
        
   
class about(QtWidgets.QMainWindow):
    def __init__(self):
        super(about, self).__init__()        
        uic.loadUi('about.ui', self)

        self.setWindowIcon(QtGui.QIcon('window_logo.png'))
        
class Login(QtWidgets.QMainWindow):
    def __init__(self):
        super(Login, self).__init__()        
        uic.loadUi('user_login.ui', self)
        self.Ui = Ui()
        self.EditMotorcycles = EditMotorcycles()
    
        self.signup_page.clicked.connect(lambda x: self.Pages.setCurrentWidget(self.register_page))
        self.login_page_btn.clicked.connect(lambda x: self.Pages.setCurrentWidget(self.login_page))
        
        self.signup_button.clicked.connect(self.register_user)
        self.login_button.clicked.connect(self.login)
        
        self.show()
        
    def register_user(self):
        email = self.email_register_input.text()
        username = self.username_register_input.text()
        password = self.password_register_input.text()
        
        if not email or not username or not password:
            print('vazio nao da')
        else:
            cursor.execute(f"""INSERT INTO Users (email, username, password) VALUES ('{email}', '{username}', '{password}')""")
            bank.commit()

        self.email_register_input.clear()
        self.username_register_input.clear()
        self.password_register_input.clear()
        
    def login(self):
        email = self.email_login_input.text()
        password = self.password_login_input.text()
        users = cursor.execute(f"""SELECT Email, Password FROM Users WHERE Email = '{email}' AND Password = '{password}'""").fetchall()
        self.Ui = Ui()
        if users:
            self.email_register_input.clear()
            self.password_register_input.clear()
            
            motorcycles = cursor.execute(f"""SELECT Name FROM Motos WHERE Email = '{email}'""").fetchall()
            for motorcycle in motorcycles:
                self.Ui.findChild(QtWidgets.QComboBox, 'comboBox').addItem(str(motorcycle).split("('")[1].split("',)")[0])
                
            motorcycles_list.clear()
            motorcycles_list.append(email)
            self.EditMotorcycles.update()
            self.Ui.show()
            self.close()

        else:
            print('nao existe')
            

class EditMotorcycles(QtWidgets.QMainWindow):
    def __init__(self):
        super(EditMotorcycles, self).__init__()        
        uic.loadUi('edit_motorcycles.ui', self)
        self.Ui = Ui
        self.update()

        self.add_motorcycle_button.clicked.connect(self.add_motorcycle)
        self.remove_motorcycle_button.clicked.connect(self.remove_motorcycle)
    
    def update(self):
        self.listWidget.clear()
        for motorcycle in cursor.execute(f"""SELECT Name, Model FROM Motos WHERE Email = '{motorcycles_list[0]}'""").fetchall():
            self.listWidget.addItem(f'''{str(motorcycle).split("('")[1].split("',)")[0].split("',")[0]} ({str(motorcycle).split(" ")[1].split("'")[1].split("')")[0]})''')

    def add_motorcycle(self):
        model = self.model_input.text()
        name = self.name_input.text()
        cursor.execute(f"""INSERT INTO Motos (Name, Email, Model) VALUES ('{name}', '{motorcycles_list[0]}', '{model}')""")
        bank.commit()
        self.update()
        self.model_input.clear()
        self.name_input.clear()
    
    def remove_motorcycle(self):
        for item in self.listWidget.selectedItems():
            cursor.execute(f"""DELETE FROM Motos WHERE Email = '{motorcycles_list[0]}' and Name = '{item.text().split(' ')[0]}' """)
            bank.commit()
            self.listWidget.takeItem(self.listWidget.row(item))
 
    def closeEvent(self, event):
        self.listWidget.clear()
        event.accept()

app = QtWidgets.QApplication(sys.argv)     
window = Login()                            
app.exec_()   