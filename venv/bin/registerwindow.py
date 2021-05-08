from PyQt5.QtWidgets import QWidget, QPushButton, QAction, QLabel, QLineEdit, qApp, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.Qt import QLineEdit

from register import *
from protocolwindow import ProtocolWindow


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        #窗体大小不可更改
        self.w = 300
        self.h = 360
        self.setFixedSize(self.w, self.h)
        self.setWindowTitle('LiChat_注册页')
        #快速注册标签
        self.quickreg = QLabel(self)
        #昵称名标签
        self.uname = QLabel(self)
        #学号信息标签
        self.stuid = QLabel(self)
        #密码标签
        self.secret = QLabel(self)
        #协议提示标签
        self.prttip = QLabel(self)
        #昵称输入
        self.unamein = QLineEdit(self)
        #学号输入
        self.idin = QLineEdit(self)
        #密码输入
        self.secin = QLineEdit(self)
        #字体集
        self.lfont = QFont('SimHei', 24, QFont.Black)
        self.mfont = QFont('SimSong', 18, QFont.Normal)
        self.sfont = QFont('SimSong', 12, QFont.Normal)
        #协议按钮
        self.tipbtw = QPushButton(self)
        #注册按钮
        self.regbtw = QPushButton(self)
        #取消按钮
        self.cancelbtw = QPushButton(self)
        #界面内容初始化
        self.reglabinit()
        self.labinit()
        self.inputinit()
        self.regbwninit()

    #快速注册和协议提示标签初始化
    def reglabinit(self):
        self.quickreg.setText('快速注册')
        self.quickreg.setFont(self.lfont)
        self.quickreg.move(50, 30)
        self.quickreg.resize(200, 30)
        self.quickreg.setAlignment(Qt.AlignCenter)

        self.prttip.setText('请确保在确认注册前，您已仔细阅读并同意')
        self.prttip.setFont(self.sfont)
        self.prttip.move(20, 240)
        self.prttip.resize(260, 20)
        self.prttip.setAlignment(Qt.AlignCenter)

    #小标签初始化
    def labinit(self):
        labels = [self.uname, self.stuid, self.secret]
        locationy = 100
        for label in labels:
            label.setFont(self.mfont)
            label.resize(50, 20)
            label.move(50, locationy)
            locationy = locationy + 40
        self.uname.setText('昵称:')
        self.stuid.setText('学号:')
        self.secret.setText('密码:')

    #文本输入框初始化
    def inputinit(self):
        inputs = [self.unamein, self.idin, self.secin]
        locationy = 100
        for widget in inputs:
            widget.resize(150, 20)
            widget.move(100, locationy)
            locationy = locationy + 40
            widget.setMaxLength(16)

    #注册按钮初始化
    def regbwninit(self):
        #初始化用户手册按钮
        self.tipbtw.setText('用户须知及服务协议')
        self.tipbtw.resize(140, 25)
        self.tipbtw.move(80, 270)
        self.tipbtw.setFont(self.sfont)
        self.tipbtw.clicked.connect(lambda: self.openprotocol())
        #初始化注册按钮
        self.regbtw.setText('注册')
        self.regbtw.resize(60, 25)
        self.regbtw.move(40, 300)
        self.regbtw.setFont(self.sfont)
        self.regbtw.clicked.connect(lambda: self.registeract())
        #初始化取消按钮
        self.cancelbtw.setText('取消')
        self.cancelbtw.resize(60, 25)
        self.cancelbtw.move(200, 300)
        self.cancelbtw.setFont(self.sfont)
        self.cancelbtw.clicked.connect(lambda: self.close())

    #展开服务协议动作的响应
    def openprotocol(self):
        protolcolwindow = ProtocolWindow()
        protolcolwindow.show()

    #点击注册动作的响应
    def registeract(self):
        nickname = str(self.unamein.text())
        stuid = str(self.idin.text())
        password = str(self.secin.text())
        inputerror = '{}输入不能为空'
        if nickname == '':
            warn = QMessageBox.about(self, '不合法的输入', inputerror.format('昵称'))
            return
        if stuid == '':
            warn = QMessageBox.about(self, '不合法的输入', inputerror.format('学号'))
            return
        if password == '':
            warn = QMessageBox.about(self, '不合法的输入', inputerror.format('密码'))
            return
        regval = register(nickname, stuid, password)
        if regval == 0:
            warn = QMessageBox.about(self, '注册失败', '此学号已被注册')
        elif regval == 1:
            warn = QMessageBox.about(self, '注册成功', '注册成功,欢迎使用')
            self.close()
        elif regval == 2:
            warn = QMessageBox.about(self, '注册失败', '此学号不是合法的THU学号')
        else:
            warn = QMessageBox.about(self, '网络错误', '网络错误,请确保使用清华大学校园网')


