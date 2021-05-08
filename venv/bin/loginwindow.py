"""
登录界面类
用于创建登录界面
"""

from PyQt5.QtWidgets import QWidget, QPushButton, QAction, QLabel, QLineEdit, qApp, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.Qt import QLineEdit

from login import *
from registerwindow import RegisterWindow
from mainwindow import LichatWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.w = 480
        self.h = 360
        self.setFixedSize(self.w, self.h)
        self.setWindowTitle('LiChat_登录页')
        # LiChat标志标签
        self.logo = QLabel(self)
        # 学号标签
        self.stuid = QLabel(self)
        # 密码标签
        self.secret = QLabel(self)
        # 注册标签
        self.reg = QLabel(self)
        # 学号输入
        self.idin = QLineEdit(self)
        # 密码输入
        self.secin = QLineEdit(self)
        # 登录按钮
        self.logbtw = QPushButton(self)
        # 注册按钮
        self.regbtw = QPushButton(self)
        self.regwindow = RegisterWindow()
        # 字体集
        self.lfont = QFont('SimSong', 24, QFont.DemiBold)
        self.mfont = QFont('SimSong', 16, QFont.Normal)
        self.sfont = QFont('SimSong', 14, QFont.Normal)
        self.tipinit()
        self.btwinit()
        self.editinit()

    # 标签的初始化
    def tipinit(self):
        self.stuid.setText('学号:')
        self.stuid.move(100, 120)
        self.stuid.resize(60, 30)
        self.stuid.setFont(self.lfont)

        self.secret.setText('密码:')
        self.secret.move(100, 180)
        self.secret.resize(60, 30)
        self.secret.setFont(self.lfont)

        self.reg.setText('还没有注册账号？')
        self.reg.move(140, 300)
        self.reg.resize(120, 20)
        self.reg.setFont(self.sfont)

    # 按钮的初始化
    def btwinit(self):
        self.logbtw.setText('登录')
        self.logbtw.resize(120, 30)
        self.logbtw.move(180, 240)
        self.logbtw.setFont(self.mfont)
        self.logbtw.clicked.connect(lambda: self.loginevent())

        self.regbtw.setText('点我注册!')
        self.regbtw.resize(100, 25)
        self.regbtw.move(260, 295)
        self.regbtw.setFont(self.sfont)
        self.regbtw.clicked.connect(lambda: self.openreg())

    # 输出框初始化
    def editinit(self):
        self.idin.move(160, 122)
        self.idin.resize(220, 25)
        self.idin.setMaxLength(10)
        self.secin.move(160, 182)
        self.secin.resize(220, 25)
        self.secin.setEchoMode(QLineEdit.Password)

    # 登录动作
    def loginevent(self):
        response = login(str(self.idin.text()), str(self.secin.text()))
        print(response)
        if response == 0:
            reply = QMessageBox.about(self, '登录错误', '抱歉,该账号未注册,请先注册。')

        elif response == 1:
            # 成功登录
            mainwindow = LichatWindow(str(self.idin.text()), str(self.secin.text()))
            mainwindow.show()
            self.close()

        elif response == 2:
            reply = QMessageBox.about(self, '登录错误', '网络错误,请检查是否接入清华大学校园网。')

        else:
            reply = QMessageBox.about(self, '登录错误', '登录密码错误,请检查输入。')


    # 打开注册窗口
    def openreg(self):
        self.regwindow.show()

    # 重写关闭函数
    def closeEvent(self, QCloseEvent):
        self.regwindow.close()
