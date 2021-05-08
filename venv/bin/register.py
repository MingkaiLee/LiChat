"""
注册函数，数据保存在本地，为了方便和可移植性使用txt而不使用mysql
"""
import socket
import json


serverIP = '166.111.140.57'
serverport = 8000


"""
检查服务器端是否存有该ID的信息
返回标志as follows:
1.正确校验;
2.错误校验;
3.校验超时;
4.连接不可用
"""
def checkid(stuid):
    login = '{}_net2019'.format(stuid)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4.0)
    try:
        sock.connect((serverIP, serverport))
    except socket.error:
        return 4
    #具有超时处理的与服务器间的通信
    sock.send(login.encode('utf-8'))
    try:
        ans = sock.recv(1024)
    except socket.timeout:
        return 3
    if ans.decode('utf-8') == 'lol':
        sock.send(('logout'+stuid).encode('utf-8'))
        try:
            agree = sock.recv(1024)
        except socket.timeout:
            return 3
        if agree.decode('utf-8') == 'loo':
            sock.close()
            return 1
        else:
            return 2
    else:
        sock.close()
        return 2


"""
注册功能函数,检查id信息的合法性并返回相应响应
返回标志as follows:
0.此id已被注册
1.合法并且注册成功,本地已保存用户信息
2.此id不合法
3.校验超时
4.无法连接到服务器
"""
def register(nickname, stuid, password):
    #检查是否id合法，存在于服务器端
    existcheck = checkid(stuid)
    if existcheck != 1:
        return existcheck
    #检查id是否存在
    with open('../data/register.json', 'r') as idinfo:
        registered = json.load(idinfo)
    for id in registered.values():
        if stuid == id:
            return 0
    #添加用户id于已注册中
    registered['ID{}'.format(len(registered)+1)] = stuid
    #写入已注册id信息中
    with open('../data/register.json', 'w') as idinfo:
        json.dump(registered, idinfo)
    #创建新用户信息
    path = '../data/usrs/{}.json'
    initial_client = {
        'NICKNAME': nickname,
        'PASSWORD': password,
        'ICON': 'default',
        'FRIENDS': [],
        'BUNDLES': []
    }
    with open(path.format(stuid), 'w+') as info:
        json.dump(initial_client, info)
    return 1
