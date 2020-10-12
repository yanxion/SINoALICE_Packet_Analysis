# -*- encoding : utf-8 -*-
import json
import os


def read_file(file_name):
    f = open(file_name, 'r', encoding="utf-8")
    data = f.readlines()
    return data


if __name__ == "__main__":
    file_data = read_file('Wepons_list.txt')
    cnt = 0
    wepon_list = []

    for data in file_data:
        if data in wepon_list:
            pass
        else:
            wepon_list.append(data)

    print(json.dumps(wepon_list))
