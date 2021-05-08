"""
主界面类,
登录进入后的主界面,
主要内容包括动态维护好友列表,并将在线的好友上提
点击好友应该能与其聊天
进入修改个人信息窗口
查找好友
Last edited time:19/11/29
预留功能：显示群聊
"""
import threading as td
import socket
from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
                             QGridLayout, QLineEdit, QMessageBox, qApp)
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QBrush, QPixmap
from PyQt5.QtCore import *
from methods import *
from chatwindow import ChatWindow

serverIP = '166.111.140.57'
serverport = 8000

# 作为服务器端(信息接收方)的端口号
chatport = 56402

# 用于侦听添加好友信息的端口
appPortreq = 56314


# 创建多线程
class RunThread(QThread):
    update = pyqtSignal(str)
    newFriend = pyqtSignal(str)

    def __init__(self, td_type):
        super().__init__()
        self.working = True
        self.td_type = td_type

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        # 刷新好友列表线程
        if self.td_type == 'refresh':
            while self.working:
                self.update.emit('refresh')
                self.sleep(3)
        # 侦听添加好友请求线程
        elif self.td_type == 'listen':
            while self.working:
                self.newFriend.emit('newfriend')


# 好友小控件
class FriendWidget(QPushButton):
    # 开始聊天信号
    startchat = pyqtSignal(str)

    def __init__(self, fid):
        super().__init__()
        # 使用水平布局
        self.wholelayout = QHBoxLayout()
        self.w = 300
        self.h = 50
        self.state = '离线'
        self.setFixedSize(self.w, self.h)
        self.setStyleSheet("background-color:#6495ED; border-style:groove; border-width:2; border-color:black")
        self.fid = fid
        self.idshow = QLabel()
        self.stateshow = QLabel()

        self.initID()
        self.initlayout()
        self.freshState()
        # 单击与在线好友开始聊天
        self.clicked.connect(lambda: self.openChat())

    def initlayout(self):
        self.wholelayout.addWidget(self.idshow)
        self.wholelayout.addWidget(self.stateshow)
        self.setLayout(self.wholelayout)

    def initID(self):
        myfont = QFont('Roman Times', 12, QFont.Black)
        # self.idshow.setFixedSize(150, 35)
        self.idshow.setFont(myfont)
        self.idshow.setText('Friend ID:{}'.format(self.fid))
        self.idshow.show()

    def freshState(self):
        myfont = QFont('SimSong', 12, QFont.Normal)
        if isOnline(self.fid):
            self.state = '在线'
            self.stateshow.setStyleSheet('color:green')
        else:
            self.state = '离线'
            self.stateshow.setStyleSheet('color:red')
        self.stateshow.setFont(myfont)
        self.stateshow.setText('状态:{}'.format(self.state))
        self.stateshow.show()

    # 如果在线,向主程序发送打开聊天窗信号
    def openChat(self):
        if self.state == '在线':
            self.startchat.emit(self.fid)


# 群聊小控件
# class BundleWidget(QWidget):


# 主窗口类
class LichatWindow(QWidget):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    def __init__(self, uid, password):
        super().__init__()

        # 窗口及用户基本信息配置
        self.uid = uid
        self.password = password
        self.w = 360
        self.h = 450
        self.setFixedSize(self.w, self.h)
        self.setWindowTitle('Lichat-{}'.format(self.uid))
        # 头像和个人信息控件
        self.faceicon = QLabel()
        self.idshow = QLabel()
        # 搜索好友的控件
        self.addfriendtext = QLineEdit()
        self.searchbtw = QPushButton()
        # 翻页按钮
        self.last = QPushButton()
        self.next = QPushButton()

        # 好友信息
        self.friends = []
        # 好友总数
        self.friends_num = 0
        # 好友页数
        self.page_num = 1
        # 当前页码
        self.page_now = 1

        # 聊天窗口列表
        self.chatwindows = []

        # 总布局
        self.wholelayout = QVBoxLayout()
        # 个人信息布局(子布局)
        self.mylayout = QVBoxLayout()
        self.mlg = QWidget()
        self.mlg.setLayout(self.mylayout)
        # 动态好友列表布局(子布局)
        self.dlayout = QVBoxLayout()
        self.dlg = QWidget()
        self.dlg.setLayout(self.dlayout)
        # 翻页和查找好友布局(子布局)
        self.flayout = QGridLayout()
        self.flg = QWidget()
        self.flg.setLayout(self.flayout)

        # 初始化好友列表
        self.initfriends()

        # 维护好友列表线程
        self.freshfriendThread = RunThread('refresh')
        self.freshfriendThread.update.connect(lambda: self.refresh())
        self.freshfriendThread.start()
        # 侦听好友请求线程
        """
        self.newfriendThread = RunThread('listen')
        self.newfriendThread.newFriend.connect(lambda: friendReq(self.uid))
        self.newfriendThread.start()
        """
        self.newfriendTd = td.Thread(target=self.friendReq, kwargs=({'uid': self.uid}))
        self.newfriendTd.setDaemon(True)
        self.newfriendTd.start()
        # 侦听聊天请求线程
        self.newchatTd = td.Thread(target=self.listenchat)
        self.newchatTd.setDaemon(True)
        self.newchatTd.start()

        self.initlayout()

    # 初始化个人信息栏
    def initmlg(self):
        # 创建头像并添加至个人布局
        faceinfo = getInfo('ICON', self.uid)
        faceimg = QPixmap('../data/lib/{}.jpg'.format(faceinfo))
        self.faceicon.setPixmap(faceimg)
        self.faceicon.setFixedSize(60, 60)
        self.mylayout.addWidget(self.faceicon, 1, Qt.AlignCenter)
        font = QFont('Roman Times', 16, QFont.DemiBold)
        self.idshow.setFont(font)
        self.idshow.setText('ID:{}'.format(self.uid))
        self.idshow.setAlignment(Qt.AlignCenter)
        self.idshow.setFixedSize(300, 20)
        self.mylayout.addWidget(self.idshow, 1, Qt.AlignCenter)

    # 初始化添加好友和通讯录翻页按钮
    def initflg(self):
        # 设置文本框
        self.addfriendtext.setMaxLength(10)
        self.addfriendtext.setFixedSize(200, 18)
        self.flayout.addWidget(self.addfriendtext, 0, 0, 1, 4, Qt.AlignVCenter)
        # 设置添加好友按钮
        self.searchbtw.setText('添加好友')
        self.searchbtw.setFixedSize(100, 20)
        # self.searchbtw.clicked.connect(lambda: self.addfriend())
        self.flayout.addWidget(self.searchbtw, 0, 4, Qt.AlignHCenter)
        # 设置翻页按钮
        self.last.setText('上一页')
        self.next.setText('下一页')
        self.last.setFixedSize(100, 20)
        self.next.setFixedSize(100, 20)
        self.flayout.addWidget(self.last, 1, 0, 1, 2)
        self.flayout.addWidget(self.next, 1, 4, 1, 2)
        self.last.clicked.connect(lambda: self.lastact())
        self.next.clicked.connect(lambda: self.nextact())

    # 初始化所有布局
    def initlayout(self):
        self.wholelayout.setSpacing(5)
        self.wholelayout.addWidget(self.mlg)
        self.wholelayout.addWidget(self.dlg)
        self.wholelayout.addWidget(self.flg)
        self.initmlg()
        self.initflg()
        self.setLayout(self.wholelayout)

    # 初始化好友列表
    def initfriends(self):
        self.friends = getInfo('FRIENDS', self.uid)
        friends_num = len(self.friends)
        self.page_num = int(friends_num / 4) + 1
        # 本页控件数
        page = self.page_num - self.page_now
        cards_num = friends_num - page * 4
        for i in range(cards_num):
            friendcard = FriendWidget(self.friends[i + page * 4])
            friendcard.startchat.connect(self.openchatwindow)
            self.dlayout.addWidget(friendcard, 1, Qt.AlignCenter)


    # 实时刷新好友列表
    def refresh(self):
        self.friends = getInfo('FRIENDS', self.uid)
        friends_num = len(self.friends)
        self.page_num = int(friends_num / 4) + 1
        # 删除过去的好友状态信息
        for x in range(self.dlayout.count()):
            # self.dlayout.itemAt(x).widget().deleteLater()
            self.dlayout.itemAt(x).widget().freshState()

    # 添加好友
    def addfriend(self):
        friendid = self.addfriendtext.text()
        sig = getFriend(self.uid, friendid)
        if sig == 0:
            reply = QMessageBox.about(self, '添加失败', 'Ta已经是您的好友了呢^^')

        elif sig == 1:
            reply = QMessageBox.about(self, '添加成功', '成功啦,祝贺您找到了新朋友~')

        elif sig == 2:
            reply = QMessageBox.about(self, '添加失败', '抱歉,对方不在线,无法添加TT')

        elif sig == 3:
            reply = QMessageBox.about(self, '添加失败', '好烦,网络出问题啦,请确保接入清华大学校园网!')

        else:
            reply = QMessageBox.about(self, '添加失败', '呐呐,好像不是一个正确的id呢，再检查下吧~')

    # 好友页翻至上一页
    def lastact(self):
        page_now = self.page_now - 1
        if page_now == 0:
            page_now = self.page_num
        self.page_now = page_now
        self.friends = getInfo('FRIENDS', self.uid)
        friends_num = len(self.friends)
        self.page_num = int(friends_num / 4) + 1
        # 删除过去的好友状态信息
        for x in range(self.dlayout.count()):
            self.dlayout.itemAt(x).widget().deleteLater()
        # 本页控件数
        page = self.page_num - self.page_now
        cards_num = friends_num - page * 4
        for i in range(cards_num):
            friendcard = FriendWidget(self.friends[i + page * 4])
            friendcard.startchat.connect(self.openchatwindow)
            self.dlayout.addWidget(friendcard, 1, Qt.AlignCenter)

    # 好友页翻至下一页
    def nextact(self):
        page_now = self.page_now + 1
        if page_now > self.page_num:
            page_now = 1
        self.page_now = page_now
        self.friends = getInfo('FRIENDS', self.uid)
        friends_num = len(self.friends)
        self.page_num = int(friends_num / 4) + 1
        # 删除过去的好友状态信息
        for x in range(self.dlayout.count()):
            self.dlayout.itemAt(x).widget().deleteLater()
        # 本页控件数
        page = self.page_num - self.page_now
        cards_num = friends_num - page * 4
        for i in range(cards_num):
            friendcard = FriendWidget(self.friends[i + page * 4])
            friendcard.startchat.connect(self.openchatwindow)
            self.dlayout.addWidget(friendcard, 1, Qt.AlignCenter)

    # 打开一个聊天窗口
    def openchatwindow(self, connect):
        flag = True
        for x in self.chatwindows:
            if x.friend_id == connect:
                flag = False
                break
        if flag:
            chatwindow = ChatWindow(connect, self.uid)
            chatwindow.clssig.connect(self.closechat)
            self.chatwindows.append(chatwindow)
            chatwindow.show()

    # 在端口56401上侦听连接请求
    def listenchat(self):
        self.sock.bind((getIP(), chatport))
        self.sock.listen(4)
        while True:
            # 为聊天分配一个新套接字
            connectionSocket, addr = self.sock.accept()
            sentence = connectionSocket.recv(1024).decode('utf-8')
            # 是否是请求聊天指令
            if len(sentence) > 0 and sentence[0] == 'c':
                friend_id = sentence.strip('c')
                print(friend_id)
                # 聊天窗口已打开,才能进行通信
                # 把接受套接字分配给对应的窗口
                flag = False
                for x in self.chatwindows:
                    print('calling' + x.friend_id)
                    if x.friend_id == friend_id:
                        flag = True
                        x.getrecvsock(connectionSocket)
                        break
                if flag:
                    print('connected')
                    connectionSocket.send('y'.encode('utf-8'))
                else:
                    print('no')
                    connectionSocket.send('f'.encode('utf-8'))
                    # 若未打开聊天窗口,则关闭与对方的套接字
                    connectionSocket.close()
            # 是否是结束聊天指令
            elif len(sentence) > 0 and sentence[0] == 'e':
                friend_id = sentence.strip('e')
                for x in self.chatwindows:
                    if x.friend_id == friend_id:
                        x.endchat()

    def friendReq(self, uid):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定套接字的端口到接受好友申请端口号
        sock.bind((getIP(), appPortreq))
        sock.listen(4)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        while True:
            connectionSocket, addr = sock.accept()
            req = connectionSocket.recv(1024).decode('utf-8')
            req.strip('a')
            addFriend(uid, req)
            connectionSocket.close()

    # 实时查看是否有聊天窗口关闭的线程
    def closechat(self, connect):
        for x in self.chatwindows:
            if x.friend_id == connect:
                self.chatwindows.remove(x)

    def closeEvent(self, QCloseEvent):
        reply = QMessageBox.question(self, '退出程序',
                                     "确认要退出吗？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((serverIP, serverport))
            sock.send('logout{}'.format(self.uid).encode('utf-8'))
            QCloseEvent.accept()
            qApp.quit()
        else:
            QCloseEvent.ignore()
