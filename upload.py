import json
import os
import requests
from goto import with_goto
from PIL import Image


def isImg(file):
    if (file.lower().endswith(('.bmp', '.webp', '.png', '.jpg', '.gif'))):
        return True
    else:
        return False


realpath = "D:\\BaiduNetdiskDownload\\test"  # 需要遍历的目录，末尾不要带/
picPostList = []
stack = []
stack.append(realpath)
# 处理栈当栈为空时结束循环
while len(stack) != 0:
    # 从栈里取数据
    dirpath = stack.pop()
    # 目录下所有文件
    fileslist = os.listdir(dirpath)
    # 处理所有文件，如果是普通文件则打印，如果是目录则压栈
    for filename in fileslist:
        fileAbspath = os.path.join(dirpath, filename)
        # print(fileAbspath)
        if os.path.isdir(fileAbspath):
            # 是目录就压栈
            print("目录: ", filename)
            stack.append(fileAbspath)
        else:
            w = isImg(fileAbspath)
            if w:
                print("图片文件: ", fileAbspath)
                picPostList.append(fileAbspath)
            else:
                print("其他文件: ", fileAbspath)

print("\n\n")


@with_goto
def postImg(picPostList):
    succNum = 0
    APIKey = "xxx" # 此处填写你的key
    url = "http://域名/api/1/upload/?key=" + APIKey + "&format=json" # 此处填写你的域名

    label.begin
    failNum = 0
    while len(picPostList) - failNum != 0:
        localPic = picPostList.pop()
        localFile = {'source': (localPic, open(localPic, 'rb'))}

        try:
            r = requests.post(url, files=localFile)
            responCode = r.status_code
        except:
            picPostList.insert(0, localPic)
            failNum += 1
            print('网络异常，加入失败队列')
        else:
            if responCode == 200:
                if json.loads(r.text)["status_code"] == 200:
                    print("\n" + json.loads(r.text)["image"]["original_filename"] + '   上传成功:   ' +
                          json.loads(r.text)["image"]["date"] + "\n" + localPic + "\n" + json.loads(r.text)["image"][
                              "url"])
                    succNum += 1
                    r.close()
                else:
                    picPostList.insert(0, localPic)
                    print("\n" + localPic + '\n上传失败! 返回值:   ' + json.loads(r.text)["status_code"] + "\n返回信息: " +
                          json.loads(r.text)["status_txt"] + "\n" + json.loads(r.text)["error"]["message"])
                    failNum += 1
                    r.close()
            elif responCode == 413:
                picPostList.insert(0, localPic)
                print("上传失败，原因：文件过大！即将开始压缩操作…")

                im = Image.open(localPic)  # 返回一个Image对象
                imgSize = os.path.getsize(localPic) / 1048576  # 计算图片Mb
                print("压缩前图片大小: " + str(imgSize) + "Mb")

                # size的两个参数
                width, height = im.size[0], im.size[1]
                # 用于保存压缩过程中的temp路径,每次压缩会被不断覆盖
                newPath = realpath + '/compress/temp.jpg'

                while imgSize >= 50:
                    width, height = round(width * 0.95), round(height * 0.95)
                    print(width, height)
                    im = im.resize((width, height), Image.ANTIALIAS)
                    im.save(newPath)
                    imgSize = os.path.getsize(newPath) / 1048576

                failNum += 1
                r.close()

                # 压缩完成备份原文件保存新文件待重新上传
                srcPath = realpath + "/compress/" + os.path.basename(localPic)

                os.rename(newPath, srcPath)

    print('成功：' + str(succNum), '失败' + str(failNum))
    print('如果您已经处理好上传失败的文件，请选择以下操作')
    print('1：继续上传失败文件；2：终止程序，不再上传')
    selectNum = input()
    if selectNum == '1':
        goto.begin
    elif selectNum == '2':
        print('程序终止')
    else:
        print('请输入正确的数字')


postImg(picPostList)
