# -*- coding: utf-8 -*-

import requests
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

prefix = '!!BLH'
live_room = []
prev_data = []
now_list = []
doloop = True
path = './plugins/blh/live_room_id_list.text'
helpmsg = '''§b----BiliLiveHelper----§r
''' + prefix + '''显示帮助信息
''' + prefix + ''' list 查看可用成员直播间列表
''' + prefix + ''' list now 查看目前订阅的成员直播间列表
''' + prefix + ''' start 编号 开启对应直播间弹幕
''' + prefix + ''' stop 编号 关闭对应直播间弹幕
''' + prefix + ''' stop all 关闭所有直播间弹幕
''' + prefix + ''' reload 重载直播间列表配置文件
'''


def post_info_data(num):
    from_data = {
        'roomid': int(live_room[num]['roomid']),
        'csrf_token': '',
        'visit_id': ''
    }
    return from_data


def post_data_url(data):
    url = 'https://api.live.bilibili.com/ajax/msg'
    response = requests.post(url, data=data)
    return response

def load_live_room_list(server):
    global live_room
    global prev_data
    global now_list
    now_list = []
    live_room = []
    prev_data = []
    with open('./plugins/blh/live_room_id_list.txt', 'r') as f:
        for line in f:
            (num, roomid, name) = line.strip().split()
            live_room.append({'num': num, 'roomid': roomid, 'name': unicode(name, 'gbk')})
            prev_data.append([])
            prev_data[-1] = post_data_url(post_info_data(-1)).json()['data']['room']
        server.say('§b[BLH]§r直播间列表重载成功')

def onServerInfo(server, info):
    global now_list
    global prev_data
    if (info.isPlayer == 1):
        if (info.content.startswith('!!blh') or info.content.startswith('!!BLH')):
            args = info.content.split(' ')
            if len(args) == 1:
                for line in helpmsg.splitlines():
                    server.tell(info.player, line)
            elif len(args) == 2 and args[1] == 'list':
                for each_liveroom in live_room:
                    server.say('编号' + str(each_liveroom['num']) + '   ' + str(each_liveroom['name']) + '的直播间')
            elif len(args) == 2 and args[1] == 'reload':
                load_live_room_list(server)
            elif len(args) == 3 and args[1] == 'list' and args[2] == 'now':
                if len(now_list) == 0:
                    server.say('无订阅直播间')
                else:
                    server.say('已订阅的直播间:')
                    for each in now_list:
                        server.say(live_room[each]['name'])
            elif len(args) == 3 and args[1] == 'start':
                try:
                    if int(args[2]) in now_list:
                        server.say(live_room[int(args[2])]['name'] + '的直播间已经被订阅！')
                    else:
                        now_list.append(int(args[2]))
                        prev_data[int(args[2])] = post_data_url(post_info_data(int(args[2]))).json()['data']['room']
                        server.say('已订阅' + live_room[int(args[2])]['name'] + '的直播间')
                except:
                    server.say('§b[BLH]§r输入错误')
            elif len(args) == 3 and args[1] == 'stop':
                if args[2] == 'all':
                    now_list = []
                    server.say('已清除所有直播间')
                elif int(args[2]) not in now_list:
                    server.say('未订阅对应编号的直播间')
                else:
                    now_list.remove(int(args[2]))
                    server.say('已取订' + live_room[int(args[2])]['name'] + '的直播间')


def onServerStartup(server):
    load_live_room_list(server)
    live_room_connection(server)

def live_room_connection(server):
    global now_list
    global isopen
    while True:
        try:
            server.say("[BLH]已上线")
            while doloop:
                isopen = True
                for each in now_list:
                    try:
                        post_data = post_info_data(each)
                        response = post_data_url(post_data)
                        data = response.json()['data']['room']
                        new = [i for i in data if i not in prev_data[each]]
                        for each_one in new:
                            server.say('§b[BLH]§r§c[' + live_room[each]['name'] + ']§r' + each_one['nickname'] + ':' + each_one[
                                'text'])
                        prev_data[each] = data
                    except:
                        print("[BLH]通信失败")
                        continue
                time.sleep(1)
        except Exception:
            if isopen:
                isopen = False
                server.say("[BLH]已下线")

if __name__ == "__main__":
    live_room_connection(None)