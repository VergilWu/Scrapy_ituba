import json
import os
import time

import requests


def find_file(file_dir):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            # 之前爬取的只有图片所以不用过滤
            # if os.path.splitext(file)[1] == '.jpeg' or '.png' or 'jpg':
            L.append(os.path.join(root, file))
    return L


time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

if not os.path.exists("pics_path.txt"):
    all_file = open('pics_path.txt', 'w')
    for line in find_file('D:\\Projects\\Desktop'):  # 查询路径
        all_file.writelines(line + '\n')
    all_file.close()
else:
    APIKey = "xxxxx"  # 图床api
    url = "http://xxxxx/api/1/upload/?key=" + APIKey + "&format=json"  # 域名

    all_file = open("pics_path.txt", mode='r')
    for all_line in all_file:
        localFile = {'source': (all_line.strip('\n'), open(all_line.strip('\n'), 'rb'))}
        r = requests.post(url, files=localFile)
        if json.loads(r.text)["status_code"] == 200:
            uploaded_file = open('成功列表.txt', 'a')
            uploaded_file.writelines(
                '\n' + time + '\n' + all_line + '\n' + json.loads(r.text)["image"][
                    "url"] + '\n' + '--------------' + '\n')
            uploaded_file.close()

            with open("pics_path.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open("pics_path.txt", "w", encoding="utf-8") as f_w:
                for line in lines:
                    if all_line in line:
                        continue
                    f_w.write(line)

            print(time + '\n' + "上传成功: " + all_line)

            continue
        else:
            upload_fail_file = open('失败列表.txt', 'a')
            upload_fail_file.writelines(time + '\n' + all_line + '\n')
            upload_fail_file.close()

            print(time + '\n' + "上传失败: " + all_line)
