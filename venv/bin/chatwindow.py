"""
聊天界面类
用于创建P2P聊天界面
"""
from PyQt5.QtWidgets import (QWidget, QPushButton, QAction, QLabel, QTextEdit, qApp, QMessageBox, QTextBrowser,
                             QGridLayout, QFileDialog)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import *
from PyQt5.Qt import QLineEdit
from chat import *
from methods import *
import socket
import datetime
import time
import threading as td
import os


serverIP = '166.111.140.57'
serverport = 8000
# 作为服务器端(信息接收方)的端口号
chatport = 56401


class ChatWindow(QWidget):
    # 聊天显示框发消息信号
    msgsig = pyqtSignal(str)
    # 给主窗口传递的关闭信号
    clssig = pyqtSignal(str)

    # 发送套接字
    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 主线程运行标志
    isrunning = True

    # 连接检查周期
    terms = 5

    # 是否提示过连接正常标志
    lastok = False

    def __init__(self, friend_id, uid, ):
        super().__init__()
        self.friend_id = friend_id
        self.uid = uid
        # 发送和接受的套接字
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 是否能够通信的标志,双重验证
        # imok = True 表示本人作为c,对方作为s已建立
        # urok = True 表示本人作为s,对方作为c已建立
        self.imok = False
        self.urok = False
        # 基本信息
        self.w = 450
        self.h = 450
        self.setFixedSize(self.w, self.h)
        self.setWindowTitle('Chatting with{}'.format(self.friend_id))
        # 好友头像及学号信息
        self.friend_icon = QLabel()
        self.friend_idshow = QLabel()
        # 聊天显示框
        self.msgbrowser = QTextBrowser()
        # 信号连接到显示框
        self.msgsig.connect(self.msgappend)
        # 聊天输入框
        self.msginputer = QTextEdit()
        # 聊天发送按钮
        self.sendmsg = QPushButton()
        # 文件发送按钮
        self.sendfile = QPushButton()
        # 总体网格布局
        self.layout = QGridLayout()
        # 界面初始化
        self.initlabel()
        self.inittexter()
        self.initbtw()
        self.setLayout(self.layout)
        # 建立通信的线程
        self.tcThread = td.Thread(target=self.isclear)
        self.tcThread.setDaemon(True)
        self.tcThread.start()
        # 接受信息的线程
        self.gmThread = td.Thread(target=self.getmsg)
        self.gmThread.setDaemon(True)
        self.gmThread.start()
        # 发送按钮功能连接
        self.sendmsg.clicked.connect(lambda: self.sendmessage())
        # 选择文件并发送按钮功能连接
        self.sendfile.clicked.connect(lambda: self.sendFile())

    # 头像及ID初始化
    def initlabel(self):
        # 创建头像并添加至个人布局
        faceinfo = getInfo('ICON', self.friend_id)
        faceimg = QPixmap('../data/lib/{}.jpg'.format(faceinfo))
        self.friend_icon.setPixmap(faceimg)
        self.friend_icon.setFixedSize(60, 60)
        self.layout.addWidget(self.friend_icon, 1, 6, 2, 3, Qt.AlignCenter)
        font = QFont('Roman Times', 12, QFont.DemiBold)
        self.friend_idshow.setFont(font)
        self.friend_idshow.setText('ID:{}'.format(self.friend_id))
        self.friend_idshow.setAlignment(Qt.AlignCenter)
        self.friend_idshow.setFixedSize(120, 20)
        self.layout.addWidget(self.friend_idshow, 3, 6, 1, 3, Qt.AlignCenter)

    # 文本框初始化
    def inittexter(self):
        self.msgbrowser.setFixedSize(300, 300)
        self.layout.addWidget(self.msgbrowser, 0, 0, 6, 6, Qt.AlignCenter)
        self.msginputer.setFixedSize(300, 100)
        self.layout.addWidget(self.msginputer, 6, 0, 1, 6, Qt.AlignCenter)

    # 按钮初始化
    def initbtw(self):
        self.sendmsg.setText('发送(Enter)')
        self.sendmsg.setShortcut('return')
        self.sendmsg.setFixedSize(100, 30)
        self.layout.addWidget(self.sendmsg, 6, 6, 1, 3, Qt.AlignCenter)
        self.sendfile.setText('文件传输')
        self.sendfile.setFixedSize(100, 30)
        self.layout.addWidget(self.sendfile, 8, 6, 1, 3, Qt.AlignCenter)

    # 接受套接字初始化
    def getrecvsock(self, sock):
        self.recvsock = sock
        # 如果接收套接字被成功初始化，说明已成功建立连接
        self.urok = True

    # 接受关闭聊天的动作
    def endchat(self):
        self.recvsock.close()
        self.sendsock.close()
        self.imok = False
        self.urok = False
        self.msgsig.emit('系统' + gettime() + ':\n')
        self.msgsig.emit('对方已断开连接,请关闭该窗口\n')
        # self.msgbrowser.append('系统' + gettime() + ':\n')
        # self.msgbrowser.append('连接已断开,请关闭窗口\n')

    # 尝试进行聊天的动作
    def trychat(self):
        self.msgsig.emit('系统' + gettime() + ':\n')
        self.msgsig.emit('等待对方建立连接...\n')
        response = self.buildconnection()
        if response == 0:
            # self.msgsig.emit('系统' + gettime() + ':\n')
            # self.msgsig.emit('对方成功连接\n')
            self.imok = True
        else:
            self.msgsig.emit('系统' + gettime() + ':\n')
            self.msgsig.emit('连接超时，将重试\n')

    # 检查连接的线程
    def isclear(self):
        while self.isrunning:
            if not self.imok:
                self.terms = 5
                self.trychat()
            elif not self.urok:
                self.terms = 5
                self.msgsig.emit('系统' + gettime() + ':\n')
                self.msgsig.emit('对方连接建立失败,尝试关闭窗口后重试\n')
            else:
                if not self.lastok:
                    self.msgsig.emit('系统' + gettime() + ':\n')
                    self.msgsig.emit('连接正常\n')
                    self.lastok = True
                self.terms = self.terms * 2
            time.sleep(self.terms)

    # 接受消息的线程
    def getmsg(self):
        while self.isrunning:
            # print('getting message')
            # urok能收到对方的信息
            while self.urok:
                try:
                    coded_msg = self.recvsock.recv(1024)
                except socket.error:
                    continue
                # 接收对方已退出的信号
                if coded_msg.decode('utf-8') is 'e':
                    self.endchat()
                    return
                # 接收传文件的信号
                elif coded_msg.decode('utf-8')[0] is 'f':
                    self.msgsig.emit('系统' + ',' + gettime() + '\n')
                    self.msgsig.emit('对方正在向你传输文件...\n')
                    whole = coded_msg.decode('utf-8')
                    filename, unused, length = whole.partition('&len&')
                    filename = filename.lstrip('f')
                    length = int(length)
                    newfile = open('../data/files/'+filename, 'wb+')
                    time = 0
                    while True:
                        mes = self.recvsock.recv(1024)
                        if mes:
                            newfile.write(mes)
                            time += len(mes)
                            if time == length:
                                self.msgsig.emit('系统,' + gettime() + '\n')
                                self.msgsig.emit('文件{}传输完成\n'.format(filename))
                                # 提示对方已接受到文件
                                cmd = 'o'
                                cmd = cmd.encode('utf-8')
                                self.sendsock.send(cmd)
                                break
                elif coded_msg.decode('utf-8') is 'o':
                    self.msgsig.emit('系统,' + gettime() + '\n')
                    self.msgsig.emit('文件传输完毕\n')
                    continue
                # 接收普通聊天内容
                else:
                    t, msg = getmsg(coded_msg)
                    print(coded_msg.decode('utf-8'))
                    self.msgsig.emit(self.friend_id + ',' + t + ':\n')
                    self.msgsig.emit(msg + '\n')

    # 发送消息
    def sendmessage(self):
        if self.imok:
            message = self.msginputer.toPlainText()
            print(message)
            self.msgsig.emit(self.uid + ',' + gettime() + ':\n')
            self.msgsig.emit(message + '\n')
            self.msginputer.clear()
            coded_msg = tomsg(message)
            self.sendsock.send(coded_msg)

    # 消息显示框附加显示消息
    def msgappend(self, connect):
        self.msgbrowser.append(connect)

    # 发送文件
    def sendFile(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, '选择文件', os.getcwd())
        # print(fileName)
        if fileName:
            fileSize = str(os.path.getsize(fileName))
            print(fileSize)
            pathName, pureName = os.path.split(fileName)
            print(pureName)
            # 依据本人的简单协议来提示对面将传输文件
            info = 'f{}&len&{}'.format(pureName, fileSize).encode('utf-8')
            self.sendsock.send(info)
            f = open(fileName, 'rb')
            self.msgsig.emit('系统,' + gettime() + ':\n')
            self.msgsig.emit('正在向对方发送文件,请不要发送信息\n')
            for line in f:
                self.sendsock.send(line)



    """
    尝试建立连接
    返回值定义:
    0.成功建立连接
    1.未能建立连接
    """

    def buildconnection(self):
        # 向服务器请求好友的IP地址
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(4.0)
        try:
            sock.connect((serverIP, serverport))
        except socket.error:
            return 1
        request = 'q{}'.format(self.friend_id)
        sock.send(request.encode('utf-8'))
        try:
            response = sock.recv(1024)
        except socket.error:
            return 1
        response = response.decode('utf-8')
        print(response)
        if response is 'n':
            return 1
        # 开始与好友建立连接
        tempsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print('yes')
            tempsock.connect((response, chatport))
            # self.sendsock.connect((response, chatport))
        except socket.error:
            print('error')
            return 1
        cmd = 'c' + self.uid
        print(cmd)
        tempsock.send(cmd.encode('utf-8'))
        # self.sendsock.send(cmd.encode('utf-8'))
        try:
            response = tempsock.recv(1024)
            # response = self.sendsock.recv(1024)
        except socket.error:
            return 1
        response = response.decode('utf-8')
        if response == 'y':
            print('get response from server.')
            self.sendsock = tempsock
            return 0
        else:
            tempsock.close()
            # self.sendsock.close()
            return 1

    # 重写关闭窗体事件,以确保不会对已关闭的套接字重复操作并确保关闭所有不用套接字
    def closeEvent(self, QCloseEvent):
        reply = QMessageBox.question(self, '退出聊天',
                                     "确认要关闭该聊天？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 通知对方退出连接
            # tempsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.urok and self.imok:
                cmd = 'e'
                cmd = cmd.encode('utf-8')
                # tempsock.connect((serverIP, serverport))
                # tempsock.send(cmd)
                self.sendsock.send(cmd)
                # 清理套接字
                self.sendsock.close()
                self.recvsock.close()
                self.urok = False
                self.imok = False
            # 关闭线程
            self.isrunning = False
            # 给主窗口发送信号已关闭该窗口,唯一辨识标志为friend_id
            self.clssig.emit(self.friend_id)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()



