from __future__ import print_function
import sys
import json
import collections
import random
import pdb


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
        """
        goals like: [1] 问 日期 ( User 主动 问 日期 ， Bot 根据 『 参考 知识 』 的 『 聊天   日期 』 回答 ， 然后 User 满足 并 好评 ) 
        --> [2] 关于 明星 的 聊天 ( Bot 主动 ， 从 『 周杰伦 』 的 生日 开始 聊 ， 根据 给定 的 明星 信息 聊   『 周杰伦 』   相关 内容 
        ， 至少 要 聊 2 轮 ， 避免 话题 切换 太 僵硬 ， 不够 自然 ) --> [3] 音乐 推荐 ( Bot 主动 ， Bot 使用   『 免费教学录像带 』   
        的 某个 评论 当做 推荐 理由 来 推荐   『 免费教学录像带 』 ， User 接受 。 需要 聊 2 轮 ) --> [4] 播放 音乐 ( Bot 主动 询问 是否
         播放 ， User 同意 后 ， Bot 播放   『 免费教学录像带 』 ) --> [5] 再见
        """
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
            if key not in keyword_list:
                continue
            tmp_entity = user_profile[key]
            if isinstance(tmp_entity, list):
                for k in tmp_entity:
                    profile_entity_list.add(k.strip())
            else:
                profile_entity_list.add(tmp_entity.strip())
        profile_entity_list = list(profile_entity_list)
        if len(goals) != sum(label):
            continue
        first_goal = goals[0].strip().split(']', 1)[1].split('(', 1)[0]  # Need testing
        # Set dialog flag
        for i in range(len(label)):
            if first_goal == '寒暄':
                if i % 2 == 0:
                    dialog_flag = 'Bot'
                else:
                    dialog_flag = 'User'
            else:
                if i % 2 != 0:
                    dialog_flag = 'Bot'
                else:
                    dialog_flag = 'User'

            if label[i] == 1:
                current_goal = goals[count - 1].split('[{0}]'.format(count))[-1]  # remove label like [1], [2]
                domain = current_goal.split('(', 1)[0]  # like ' 问 日期 '
                if "『" and "』" not in current_goal:
                    output_file.write(conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + domain + '\t' +\
                                      str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                    current_entity_goal = domain
                else:
                    if domain in flag1:
                        tmp = current_goal.split("『")[-1].split("』", 1)[0]
                        if domain == "问日期":
                            output_file.write(conversation[i] + '\t' + str(label[i]) + '\t' +domain + '\t' + domain + '\t'\
                                              + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                            current_entity_goal = tmp + " 新闻"
                        else:
                            output_file.write(
                                conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + domain + '\t' \
                                + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                            current_entity_goal = tmp
                    elif domain in flag2:
                        tmp1 = current_goal.split("『", 1)[-1].split("』", 1)[0]
                        tmp2 = current_goal.split("『", -1)[-1].split("』", -1)[0]
                        if tmp1 not in bad_flag:
                            if flag_flag == 0:
                                output_file.write(
                                    conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + tmp1 + '\t' \
                                    + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                                current_entity_goal = tmp2
                                flag_flag = 1
                            else:
                                output_file.write(
                                    conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + tmp2 + '\t' \
                                    + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                                current_entity_goal = tmp2
                                flag_flag = 0
                        else:
                            if flag_flag == 1:
                                output_file.write(
                                    conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + current_entity_goal + '\t' \
                                    + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                            else:
                                output_file.write(
                                    conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + tmp2 + '\t' \
                                    + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                                current_entity_goal = tmp2
                    else:
                        output_file.write(
                            conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + domain + '\t' \
                            + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
                count += 1
            else:
                output_file.write(
                    conversation[i] + '\t' + str(label[i]) + '\t' + domain + '\t' + current_entity_goal + '\t' \
                    + str(kg) + '\t' + str(user_profile) + '\t' + dialog_flag + '\n')
        output_file.write('\n')
    output_file.close()




if __name__ == "__main__":
    add_label("../origin_data/resource/train.txt", '../origin_data/train_add_label.txt')
    add_label('../origin_data/resource/dev.txt', '../origin_data/dev_add_label.txt')
    process_session_data('../origin_data/train_add_label.txt', '../origin_data/train.txt')
    process_session_data('../origin_data/dev_add_label.txt', '../origin_data/dev.txt')
    # process_sample_data('../origin_data/resource/test_1.txt', '../origin_data/test.txt')
