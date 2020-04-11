# -*- coding: utf-8 -*-

import requests
import time
import sys
import json
import copy

prefix = '!!BLH'
live_room = []
prev_data = []
now_list = []
people_num = 0
reloaded = 0
doloop = True
path = './plugins/blh/live_room_id_list.json'
helpmsg = '''§b----BiliLiveHelper----§r
''' + prefix + '''显示帮助信息
''' + prefix + ''' list 查看可用成员直播间列表
''' + prefix + ''' list now 查看目前订阅的成员直播间列表
''' + prefix + ''' start 编号 开启对应直播间弹幕
''' + prefix + ''' stop 编号 关闭对应直播间弹幕
''' + prefix + ''' stop all 关闭所有直播间弹幕
''' + prefix + ''' reload 重载直播间列表配置文件
''' + prefix + ''' on/off/restart 开启/关闭/重启blh
''' + prefix + ''' stats 查询blh状态
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
    with open(path, 'r') as f:
        for line in f:
            (num, roomid, name) = line.strip().split()
            live_room.append({'num': num, 'roomid': roomid, 'name': name})
            prev_data.append([])
            prev_data[-1] = post_data_url(post_info_data(-1)).json()['data']['room']



def reload_text(num):
    global prev_data
    prev_data[num] = post_data_url(post_info_data(num)).json()['data']['room']


def onServerInfo(server, info):
    global now_list
    global prev_data
    global doloop
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
                on_unload(server)
                load_live_room_list(server)
                server.say('§b[BLH]§r直播间列表重载成功')
                doloop = True
                live_room_connection(server)
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
                        reload_text(int(args[2]))
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
            elif (info.content == '!!blh off' or info.content == '!!BLH off'):
                on_unload(server)
                server.say('§b[BLH]§r已下线')
            elif (info.content == '!!blh on' or info.content == '!!BLH on'):
                on_unload(server)
                load_live_room_list(server)
                doloop = True
                server.say('§b[BLH]§r已上线')
                live_room_connection(server)

            elif (info.content == '!!blh restart' or info.content == '!!BLH restart'):
                on_unload(server)
                load_live_room_list(server)
                doloop = True
                server.say('§b[BLH]§r已重载')
                live_room_connection(server)

            elif (info.content == '!!blh stats' or info.content == '!!BLH stats'):
                server.tell(info.player, str(doloop))

def live_room_connection(server):
    global now_list
    global reloaded
    global doloop
    global people_num

    print("[BLH]已上线")

    while doloop:
        if people_num == 0 and reloaded == 0:
            reloaded = 1
        if people_num > 0:
            if reloaded == 1:
                for a in now_list:
                    reload_text(a)
                reloaded = 0
            for each in now_list:
                try:
                    post_data = post_info_data(each)
                    response = post_data_url(post_data)
                    data = response.json()['data']['room']
                    new = [i for i in data if i not in prev_data[each]]
                    for each_one in new:
                        server.say(
                            '§b[BLH]§r§c[' + live_room[each]['name'] + ']§r' + each_one['nickname'] + ':' + each_one[
                                'text'])
                    prev_data[each] = data
                except:
                    print("[BLH]通信失败")
        time.sleep(1)

    print("[BLH]已下线")


def on_info(server, info):
    info2 = copy.deepcopy(info)
    info2.isPlayer = info2.is_player
    onServerInfo(server, info2)


def onPlayerJoin(server, player):
    global people_num
    people_num += 1


def on_player_joined(server, player):
    onPlayerJoin(server, player)


def onPlayerLeave(server, player):
    global people_num
    people_num -= 1


def on_player_left(server, player):
    onPlayerLeave(server, player)


def on_load(server, old_module):
    global people_num
    global doloop
    doloop = True
    if old_module is not None:
        people_num = old_module.people_num
    else:
        people_num = 0
    load_live_room_list(server)
    live_room_connection(server)


def on_unload(server):
    global doloop
    doloop = False
    time.sleep(1)


if __name__ == "__main__":
    live_room_connection(None)
