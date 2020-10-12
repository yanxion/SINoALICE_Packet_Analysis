# -*- coding : utf-8 -*-
import json
from bottle import route, run, static_file
import os
import time
import datetime

# 架設網頁
@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root=os.path.join(os.path.dirname(__file__), 'static'))


def web_run():
    run(host='0.0.0.0', port=8080)


def write_file(file_name, timestamp, data):
    try:
        # now = datetime.datetime.now()
        # timestamp = now.strftime("_%Y%m%d")
        file_name = file_name + "_" + timestamp + '.json'
        print(file_name)
        f = open(file_name, 'w')
        f.write(data)
    except Exception as e:
        print(e)


def read_file(file_name):
    f = open(file_name, 'r', encoding="utf-8")
    data = f.readlines()
    return data


def is_battle_history(data):  # 判斷是不是武器相關的數據
    if (data.find("公會戰艦") >= 0):
        return False
    if (data.find("召喚技能") >= 0):
        return False
    if (data.find("復活") >= 0):
        return False
    return True


def handle_member(battle_data, own_list, enemy_list):  # 判斷成員是哪一隊的
    if battle_data['isOwnGuild']:
        if not battle_data['userName'] in own_list and not battle_data['userName'] == "":
            own_list.append(battle_data['userName'])
    else:
        if not battle_data['userName'] in enemy_list and not battle_data['userName'] == "":
            enemy_list.append(battle_data['userName'])
    return own_list, enemy_list


def set_battle_member(j_data):  # 初始化敵我隊伍的成員清單列
    for username in j_data['own_user_list']:
        j_data['own_battle_list'][username] = {}
        j_data['own_battle_list'][username]['all_weapon'] = {}
    for username in j_data['enemy_user_list']:
        j_data['enemy_battle_list'][username] = {}
        j_data['enemy_battle_list'][username]['all_weapon'] = {}


def log_all_battle_data(battle_data, j_data):
    if battle_data['isOwnGuild']:
        j_data['own_battle_list'][battle_data['userName']
                                  ]['all_weapon'][battle_data['actTime']] = battle_data['readableText']
    else:
        j_data['enemy_battle_list'][battle_data['userName']
                                    ]['all_weapon'][battle_data['actTime']] = battle_data['readableText']


def log_user_weapon_type_data(battle_data, weapon, j_data):
    if battle_data['isOwnGuild']:
        try:
            j_data['own_battle_list'][battle_data['userName']][weapon['active_level'] + ': ' + weapon['name']
                                                               ][battle_data['actTime']] = battle_data['readableText']
        except:
            j_data['own_battle_list'][battle_data['userName']
                                      ][weapon['active_level'] + ': ' + weapon['name']] = {}
            j_data['own_battle_list'][battle_data['userName']][weapon['active_level'] + ': ' + weapon['name']
                                                               ][battle_data['actTime']] = battle_data['readableText']
    else:
        try:
            j_data['enemy_battle_list'][battle_data['userName']][weapon['active_level'] + ': ' + weapon['name']
                                                                 ][battle_data['actTime']] = battle_data['readableText']
        except:
            j_data['enemy_battle_list'][battle_data['userName']
                                        ][weapon['active_level'] + ': ' + weapon['name']] = {}
            j_data['enemy_battle_list'][battle_data['userName']][weapon['active_level'] + ': ' + weapon['name']
                                                                 ][battle_data['actTime']] = battle_data['readableText']


def log_user_weapon_data(battle_data, j_data):  # 偵測這筆紀錄是不是使用武器的，並回傳武器分析資訊
    with open('weapons_classify.json', 'r', encoding="utf-8") as f:
        weapon_classify = json.load(f)
    username = battle_data['userName']
    weapon_split = battle_data['readableText'].split('\n')
    weapon_des = None
    weapon_actTime = None
    try:
        if (len(weapon_split) > 1):
            if weapon_split[0].find('Combo') >= 0:
                if weapon_split[1].find('Lv') >= 0:
                    weapon_active_level = weapon_split[1][weapon_split[1].find(
                        'Lv'):weapon_split[1].find('發動')]
                    weapon_actTime = battle_data['actTime']
                    weapon_des = weapon_split[1]
            else:
                if weapon_split[0].find('Lv') >= 0:
                    weapon_active_level = weapon_split[0][weapon_split[0].find(
                        'Lv'):weapon_split[0].find('發動')]
                    weapon_actTime = battle_data['actTime']
                    weapon_des = weapon_split[0]
    except Exception as e:
        print(weapon_split)
        print(e)
        exit()
    weapon = {"name": None, "type": None,
              "skill": None, "time": None, 'active_level': None}
    if weapon_des:
        for weapon_type in weapon_classify['skill_list']:
            for weapon_skill in weapon_classify['skill_list'][weapon_type]:
                if weapon_des.find(weapon_skill) >= 1:
                    weapon['name'] = weapon_des[:weapon_des.find(weapon_skill)]
                    weapon['type'] = weapon_type
                    weapon['skill'] = weapon_skill
                    weapon['time'] = weapon_actTime
                    weapon['active_level'] = weapon_active_level
                    # print(weapon_type, ' / ', weapon, ' / ', weapon_skill)
        # print("-----------")
        if not weapon['name']:
            print(weapon_des)

    return weapon


# battle_history處理，要指定處理日期就傳入file_name, format : filename.txt
def battle_history_handle(file_name=None):
    now = datetime.datetime.now()
    date = now.strftime("_%Y%m%d")
    if file_name:
        file_data = read_file('./battle_his/' + file_name)
    else:
        file_data = read_file(
            './battle_his/get_battle_history' + date + '.txt')
        filename = 'get_battle_history' + date + '.txt'
    j_data = {}
    j_data['own_user_list'] = []
    j_data['enemy_user_list'] = []
    j_data['own_battle_list'] = {}
    j_data['enemy_battle_list'] = {}
    # 將己方公會與敵方公會的人物名稱存起來
    for json_dump_data in file_data:
        json_data = json.loads(json_dump_data)
        for battle_data in json_data['payload']['gvgBattleHistory']:
            j_data['own_user_list'], j_data['enemy_user_list'] = handle_member(
                battle_data, j_data['own_user_list'], j_data['enemy_user_list'])
    set_battle_member(j_data)

    count = 0
    # 透過user_list來建立dict，並紀錄戰鬥紀錄
    for json_dump_data in file_data:
        json_data = json.loads(json_dump_data)
        for battle_data in json_data['payload']['gvgBattleHistory']:
            if is_battle_history(battle_data['readableText']) and battle_data['userName'] == "別人笑我太鬆餅":
                print(battle_data['userName'], " : " , end='')
                print(datetime.datetime.fromtimestamp(battle_data['actTime']).strftime('%H:%M:%S'), " : ", end='')
                print(battle_data['readableText'].replace('\n', ''))

            if is_battle_history(battle_data['readableText']) and not battle_data['userName'] == "":
                weapon = log_user_weapon_data(battle_data, j_data)
                if weapon['name']:
                    log_all_battle_data(battle_data, j_data)
                    log_user_weapon_type_data(battle_data, weapon, j_data)
        # count += 1
        # if count == 1:
        #     break
    # print(json.dumps(j_data))
    return file_name, j_data


if __name__ == "__main__":
    file_name, battle_data = battle_history_handle('get_battle_history_20191209.txt')
    write_file('./static/battle_history_json',
               file_name[-12:-4], "var battle_history_json = \n" + json.dumps(battle_data))
    """
    http://140.123.97.122:8080/static/battle_history.html
    """
    # web_run()
