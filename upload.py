import json
import os
import requests
import numpy
from goto import with_goto
from PIL import Image


def isImg(file):
    if (file.lower().endswith(('.bmp', '.webp', '.png', '.jpg', '.gif'))):
        return True
    else:
        return False


realpath = "D:\\BaiduNetdiskDownload\\datu\\test"  # 需要遍历的目录，末尾不要带/
backupPath = "D:\\BaiduNetdiskDownload\\backup"  # 需要备份经处理图片的目录，末尾不要带/，不要选择其他分区的硬盘
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
                # print(picPostList)

                # 不能直接操作原文件容易出错
                fp = open(fileAbspath, 'rb')
                im = Image.open(fp)  # 返回一个Image对象
                # 后面还要用调用load函数，所以在close()前转换为numpy array类型
                pic_array = numpy.array(im)
                # 操作文件即时关闭
                fp.close()

                im = Image.fromarray(pic_array)
                img_size = os.path.getsize(fileAbspath) / 1048576  # 计算图片Mb

                # size的两个参数
                width, height = im.size[0], im.size[1]
                # 用于保存压缩过程中的temp路径,每次压缩会被不断覆盖
                new_path = realpath + '/temp.jpg'
                src_path = realpath + "/" + os.path.basename(fileAbspath)

                (filePath, tempFilename) = os.path.split(src_path)  # filepath 文件路径 tempFilename 文件名含后缀
                (shortName, extension) = os.path.splitext(tempFilename)  # shortName 文件名不含后缀 extension 后缀名

                if img_size >= 50:
                    print("图片太大: ", str(int(img_size)) + "Mb", "即将进行压缩处理...")
                    width, height = round(width * 0.95), round(height * 0.95)
                    im = im.resize((width, height), Image.ANTIALIAS)
                    # 此时im为RGBA四通道，当原图格式为3通道时会报错，需要转换
                    im = im.convert('RGB')
                    im.save(new_path)
                    img_size = os.path.getsize(new_path) / 1048576
                    print("图片实时大小: " + str(int(img_size)) + "Mb", "实时分辨率: ", width, "x", height)

                    os.renames(src_path, backupPath + "/" + tempFilename)
                    os.rename(new_path, src_path)
            else:
                print("其他文件: ", fileAbspath)

print("\n\n")


@with_goto
def postImg(picPostList):
    succNum = 0
    APIKey = "4c5f01d2378410a3b5c4e1d4a6eddafc"
    url = "http://img.vergil.com.cn/api/1/upload/?key=" + APIKey + "&format=json"
    # print("=======", picPostList)
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
            elif responCode == 400:
                print(localPic, "上传失败，原因：已存在此文件！")
                succNum += 1
                r.close()
            elif responCode == 413:
                picPostList.insert(0, localPic)
                print("上传失败，原因：文件过大！")
                failNum += 1
                r.close()

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
