# -*- coding : utf-8 -*-
from mitmproxy import ctx
import msgpack
import os
import json
import datetime


def unpackdata(msgpackData):
    return msgpack.unpackb(msgpackData,  raw=False)

def get_battle_history(url, response_data, request_data):
    try:
        response_data = unpackdata(response_data)
        request_data = unpackdata(request_data)
        print("No.", request_data['payload']['pageNo'], end=' ')
        write_file('./battle_his/get_battle_history', json.dumps(response_data))
        print("Write success.")

        # print(json.dumps(data))
        # for user_data in data['payload']['guildMemberList']:
        # print(user_data['userData']['name'])
        print(
            '----response----------------------------------------------------------------')
    except Exception as e:
        print(e)

def guild_member_list(url, response_data, request_data):
    try:
        response_data = unpackdata(response_data)
        request_data = unpackdata(request_data)
        # write_file('./group_list/guild_member_list', json.dumps(response_data))
        for data in response_data['payload']['guildMemberList']:
            print(data['userData']['playerId'], data['userData']['name'], 
            data['userData']['currentTotalPower'], data['userData']['currentJobMstId'],
            data['userData']['currentJobRoleType'], data['userData']['currentJobRolePosition'])
        # print('guild_member_list write success.')
    except Exception as e:
        print(e)

def write_file(file_name, data):
    try:
        now = datetime.datetime.now()
        timestamp = now.strftime("_%Y%m%d")
        file_name = file_name + timestamp + '.txt'
        print(file_name)
        f = open(file_name, 'a')
        f.write(data)
        f.write("\n")
        return True
    except Exception as e:
        print(e)
        return False

def request(flow):
    # ctx.log.warn(str(flow.request.headers))
    pass
    print("")

def response(flow):
    # print(flow.response)
    os.system('cls' if os.name == 'nt' else 'clear')
    url = str(flow.request.url)
    if (url.find("komoejoy") >= 0):
        if (url.find("get_battle_history") >= 0):
            get_battle_history(url, flow.response.content, flow.request.content)
        elif (url.find("guild_member_list") >= 0):
            guild_member_list(url, flow.response.content, flow.request.content)
        
