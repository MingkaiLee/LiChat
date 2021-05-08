"""
聊天界面函数包
函数及功能如下:
1.gettime()返回当期时间
2.tomsg()转换输入为标准信息交换格式并编码
3.getmsg()解码输出并分离出时间和内容
4.getIp()获取本机的IP地址
"""

import datetime
import time
import socket
import os

serverIP = '166.111.140.57'
serverport = 8000

# 作为服务器端(信息接收方)的端口号
chatport = 56401

def gettime():
    nowtime = datetime.datetime.now()
    return nowtime.strftime('%Y-%m-%d,%H:%M:%S')


def tomsg(message):
    msg = 'parse:t' + gettime() + 'a:' + message
    coded_msg = msg.encode('utf-8')
    return coded_msg


def getmsg(coded_msg):
    msg = coded_msg.decode('utf-8')
    nowtime = msg[7:26]
    content = msg[28:]
    return nowtime, content


# 获取本机的IP地址
def getIP():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

"""
返回值定义:
0.成功建立连接
1.网络错误
2.好友不在线
"""
def biuldconnection(friend_id, myport):
    # 向服务器请求好友的IP地址
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((getIP(), myport))
    sock.settimeout(4.0)
    try:
        sock.connect((serverIP, serverport))
    except socket.error:
        return 1
    request = 'q{}'.format(friend_id)
    sock.send(request.encode('utf-8'))
    try:
        response = sock.recv(1024)
    except socket.error:
        return 1
    response = response.decode('utf-8')
    sock.close()
    if response is 'n':
        return 2
    # 开始与好友建立连接
    try:
        sock.connect((response, chatport))
    except socket.error:
        return 1
    sock


"""
侦听连接请求,可视为服务器端
"""
def listenconnection(uid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((getIP(), chatport))
