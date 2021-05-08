"""
用于主界面的函数包,
包中各函数的功能如下:
isOnline:查询目标是否在线
getIP:获取本机的IP地址
getInfo:获取相应的数据
fixInfo:修改相应的数据,只能修改用户名,密码以及头像
addFriend:更新好友信息
getFriend:添加好友
friendReq:侦听添加好友的请求
createBundle:创建群聊
"""
import json
import socket
import threading

serverIP = '166.111.140.57'
serverport = 8000

# 用于侦听添加好友信息的端口
appPortreq = 56314

# 查询目标是否在线
def isOnline(stuid):
    request = 'q{}'.format(stuid)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((serverIP, serverport))
    except socket.error:
        return False
    sock.send(request.encode('utf-8'))
    response = sock.recv(1024)
    response = response.decode('utf-8')
    if response == 'n':
        return False
    else:
        return True

# 获取本机的IP地址
def getIP():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

# 获取所需的用户信息
def getInfo(infotype, uid):
    path = '../data/usrs/{}.json'.format(str(uid))
    with open(path, 'r') as f:
        info = json.load(f)
    ans = info[infotype]
    return ans

# 修改用户的个人信息
def fixInfo(infotype, uid, new):
    path = '../data/usrs/{}.json'.format(str(uid))
    with open(path, 'r') as fin:
        info = json.load(fin)
    info[infotype] = new
    with oepn(path, 'w') as fout:
        json.dump(info, fout)

# 本地添加好友信息
def addFriend(uid, friendid):
    with open('../data/usrs/{}.json'.format(uid), 'r') as fin:
        uinfo = json.load(fin)
    uinfo['FRIENDS'].append(friendid)
    with open('../data/usrs/{}.json'.format(uid), 'w') as fout:
        json.dump(uinfo, fout)

"""
添加好友功能函数，
返回值及意义如下
0.该好友已在你的好友列表中
1.对方在线且已添加完成
2.对方不在线
3.网络错误
4.该账号不存在
添加好友的指令:a+本人id
"""
def getFriend(uid, friendid):
    with open('../data/register.json', 'r') as reg:
        usrs = json.load(reg)
    flag = False
    for usr in usrs.values():
        if friendid == usr:
            flag = True
            break
    if not flag:
        return 4
    path = '../data/usrs/{}.json'.format(str(uid))
    with open(path, 'r') as fin:
        info = json.load(fin)
    friends = info['FRIENDS']
    for friend in friends:
        if friend == friendid:
            return 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4.0)
    try:
        sock.connect((serverIP, serverport))
    except socket.error:
        return 3
    request = 'q{}'.format(friendid)
    sock.send(request.encode('utf-8'))
    try:
        response = sock.recv(1024)
    except socket.error:
        return 3
    response = response.decode('utf-8')
    sock.close()
    if response == 'n':
        return 2
    reqsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        reqsock.connect((response, appPortreq))
    except socket.error:
        return 3
    request = 'a{}'.format(id)
    reqsock.send(request.encode('utf-8'))
    reqsock.close()
    addFriend(uid, friendid)
    return 1




