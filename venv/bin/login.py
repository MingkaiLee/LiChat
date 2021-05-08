import socket
import json

serverIP = '166.111.140.57'
serverport = 8000

"""
进行登录动作
返回标志as follows:
0.此ID未在本地注册
1.成功登录
2.网络错误
3.密码错误
"""


def login(stuid, password):
    flag = False
    with open('../data/register.json', 'r') as idinfo:
        users = json.load(idinfo)
    for id in users.values():
        if stuid == id:
            flag = True
            break
    if not flag:
        return 0
    with open('../data/usrs/{}.json'.format(stuid), 'r') as usr:
        usrinfo = json.load(usr)
    if usrinfo['PASSWORD'] != password:
        # print(usrinfo["PASSWORD"]+" "+password)
        return 3
    logcmd = '{}_net2019'.format(stuid)
    usrsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    usrsock.settimeout(4.0)
    try:
        usrsock.connect((serverIP, serverport))
    except socket.error:
        return 2
    usrsock.send(logcmd.encode('utf-8'))
    try:
        ans = usrsock.recv(1024)
    except socket.timeout:
        return 2
    if ans.decode('utf-8') == 'lol':
        return 1
