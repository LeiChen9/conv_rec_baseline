from __future__ import print_function
import sys
import json
import collections
import random


def is_start_with(str, start_str=['[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]']):
    for s in start_str:
        if str.startswith(s):
            return 1
    return 0


def add_label(input_filename, output_filename):
    output_file = open(output_filename, 'w')
    for line in open(input_filename, 'r').readlines():
        data = json.loads(line.strip())
        conversation = data['conversation']
        label = []
        for c in conversation:
            label.append(is_start_with(c.strip()))
        data['label'] = label  # like [1, 0, 0, 1, ...]
        output_file.write(json.dumps(data, ensure_ascii=False) + '\n')
    output_file.close()


def process_session_data(input_filename, output_filename):
    bad_flag = ["参考知识"]
    flag = ["再见", "问天气", "问时间", "天气信息推送"]
    flag1 = ["关于明星的聊天", "音乐推荐", "播放音乐", "美食推荐", "poi推荐", "电影推荐", "音乐点播", "问日期", "新闻推荐", "新闻点播", "", "", ""]
    flag2 = ["问答"]
    flag3 = ["寒暄"]

    # user_profile key
    p_r_key = ["拒绝"]
    p_p_key = ["喜欢的电影", "喜欢的明星", "喜欢的poi", "喜欢的音乐", "喜欢的新闻"]
    p_a_key = ["同意的新闻", "同意的音乐", "同意的美食", "同意的poi", "同意的电影"]
    p_key = ["接受的电影", "接受的音乐", "没有接受的电影", "没有接受的音乐"]
    list_key = ["同意的新闻", "没有接受的音乐", "接受的电影", "喜欢的明星", "接受的音乐", "没有接受的电影", "喜欢的新闻"]

    all_flag = bad_flag + flag +flag1 + flag2
    output_file = open(output_filename, 'w')
    user_profile_key_result = set()
    for line in open(input_filename, 'r'):
        flag_flag = 0
        entity_level_goal = ""
        count = 1
        data = json.loads(line.strip())
        situation = data['situation']
        conversation = data['conversation']
        goals = data['goal']
        label = data['label']
        kg = data['knowledge']
        user_profile = data['user_profile']
        goals = goals.split("-->")
        current_entity_goal = ""
        used_kg_entity = set()
        for (s, r, o) in kg:
            if r != "适合吃" and s != '聊天':
                used_kg_entity.add(s)
        used_kg_entity = list(used_kg_entity)  # turn set to list
        profile_entity_list = set()
        for key in user_profile:
            user_profile_key_result.add(key)
        for key in user_profile:
            keyword_list = p_p_key + p_a_key + p_r_key


if __name__ == "__main__":
    add_label("../origin_data/resource/train.txt", '../origin_data/train_add_label.txt')
    add_label('../origin_data/resource/dev.txt', '../origin_data/dev_add_label.txt')
    process_session_data('../origin_data/train_add_label.txt', '../origin_data/train.txt')
    process_session_data('../origin_data/dev_add_label.txt', '../origin_data/dev.txt')
    process_sample_data('../origin_data/resource/test_1.txt', '../origin_data/test.txt')
