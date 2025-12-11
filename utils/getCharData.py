from venv import create

from django.template.defaulttags import comment

from utils.getPublicData import *
import json

userList = list(getAllUserList())
bookList = list(getAllBookList())


def getHomeDataPage():
    userLen = len(userList)  # 用户总数
    maxPrice = 0  # 最高价格
    maxPriceBookName = ""  # 最高价格的书籍名称
    typeLen = []  # 书籍分类
    maxRate = 0  # 最高评分
    maxPageNum = 0  # 最多页数
    rateList = []  # 评分列表

    # 遍历书籍列表，提取数据
    for i in bookList:
        rateList.append(float(i.rate))  # 添加评分
        if maxPrice < float(i.price):  # 更新最高价格
            maxPrice = float(i.price)
            maxPriceBookName = i.title
        typeLen.append(i.tag)  # 添加分类

        if maxRate < float(i.rate):  # 更新最高评分
            maxRate = float(i.rate)
        if maxPageNum < int(i.pageNum):  # 更新最多页数
            maxPageNum = int(i.pageNum)

    # 去重并统计分类数量
    typeLen = len(list(set(typeLen)))
    # 对评分列表去重并排序
    rateList = list(set(rateList))
    rateList.sort(reverse=True)
    rateListNum = [0 for _ in range(len(rateList))]  # 初始化评分数量列表

    # 统计每个评分的数量
    for i in bookList:
        for index, j in enumerate(rateList):
            if float(i.rate) == j:
                rateListNum[index] += 1

    # 统计用户创建时间分布
    createUserDic = {}
    for u in userList:
        time = u.createTime.strftime("%Y-%m-%d")
        if time not in createUserDic:
            createUserDic[time] = 1
        else:
            createUserDic[time] += 1

    createUserList = [{"name": k, "value": v} for k, v in createUserDic.items()]

    # 提取评论列表
    commentList = []
    for i in bookList:
        comments = json.loads(i.commentList)
        commentList.extend(comments)

    # 返回所有需要的值
    return (
        userLen,
        typeLen,
        maxPrice,
        maxPriceBookName,
        maxRate,
        maxPageNum,
        rateList,
        rateListNum,
        createUserList,
        commentList
    )

#适应了密码加密
# from myApp.models import User
from django.contrib.auth.hashers import check_password, make_password

def changePassword(uname, passwordData):
    oldPwd = passwordData['oldPassword']
    newPwd = passwordData['newPassword']
    checkPwd = passwordData['checkPassword']

    try:
        user = User.objects.get(username=uname)
    except User.DoesNotExist:
        return '用户不存在'

    # ✅ 使用 check_password() 验证旧密码
    if not check_password(oldPwd, user.password):
        return '原密码不正确'

    # ✅ 确保新密码和确认密码一致
    if newPwd != checkPwd:
        return '两次密码不一致'

    # ✅ 使用 make_password() 手动加密新密码
    user.password = make_password(newPwd)
    user.save()

    return '密码修改成功'

#密码加密无适应

# def changePassword(uname, passwordData):
#     oldPwd = passwordData['oldPassword']
#     newPwd = passwordData['newPassword']
#     checkPwd = passwordData['checkPassword']
#     user = User.objects.get(username=uname)
#     if oldPwd != user.password: return '原密码不正确'
#     if newPwd != checkPwd: return '两次密码不一致'
#
#     user.password = newPwd
#     user.save()
#     return '密码修改成功'


def getTableData():
    return bookList


def getTypePieData():
    typeDic = {}
    for i in bookList:
        if typeDic.get(i.tag, -1) == -1:
            typeDic[i.tag] = 1
        else:
            typeDic[i.tag] += 1
    typeRes = []
    for k, v in typeDic.items():
        typeRes.append({'name': k, 'value': v})

    # print(typeRes)
    return typeRes


def getTypeRateData():
    typeData = {}
    for i in bookList:
        if typeData.get(i.tag, -1) == -1:
            typeData[i.tag] = 1
        else:
            typeData[i.tag] += 1
    rateData = {}
    for k, v in typeData.items():
        if rateData.get(k, -1) == -1:
            rateData[k] = []

    for i in bookList:
        for k, v in rateData.items():
            if i.tag == k:
                v.append(float(i.rate))
    print(rateData)
    for k, v in rateData.items():
        sum = 0
        for item in v:
            sum += item
        rateData[k] = round(sum / len(v), 1)
    print(rateData)

    return list(typeData.keys()), list(typeData.values()), list(rateData.values())


def getBookTypeList():
    typeList = []
    for i in bookList:
        typeList.append(i.tag)
    print(list(set(typeList)))
    return list(set(typeList))


def getBookPriceData(defaultType):
    typeBook = []
    for i in bookList:
        if defaultType == i.tag:
            typeBook.append(i)

    xData = ['15元', '30元', '50元', '100元', '200元', '200元以上']
    yData = [0] * len(xData)  # 初始化yData为0

    for i in typeBook:
        try:
            price = float(i.price)  # 将价格转换为浮动类型
        except ValueError:
            # 如果价格不能转换为浮动数值（例如有异常值），跳过这个条目
            continue

        if price < 15:
            yData[0] += 1
        elif price < 30:
            yData[1] += 1
        elif price < 50:
            yData[2] += 1
        elif price < 100:
            yData[3] += 1
        elif price < 200:
            yData[4] += 1
        else:
            yData[5] += 1  # 200元以上

    print(yData)
    return xData, yData


def getBookPageData(defaultType):
    # 筛选出符合条件的图书
    typeBook = [i for i in bookList if defaultType == i.tag]

    # 定义x轴数据和y轴数据（初始化yData为0）
    xData = ['小于150页', '小于200页', '小于400页', '小于650页', '小于800页', '800页以上']
    yData = [0] * len(xData)  # 初始化yData为0，确保索引范围正确

    # 遍历筛选出来的图书，统计各个区间的页数
    for i in typeBook:
        try:
            page_num = int(i.pageNum)  # 将页数转换为整数
        except ValueError:
            # 如果页数无法转换为整数（如数据有问题），跳过该图书
            continue

        if page_num < 150:
            yData[0] += 1
        elif page_num < 200:
            yData[1] += 1
        elif page_num < 400:
            yData[2] += 1
        elif page_num < 650:
            yData[3] += 1
        elif page_num < 800:
            yData[4] += 1
        else:
            yData[5] += 1  # 800页以上

    # 输出统计结果并返回
    print(yData)
    return xData, yData


def getCommentLenCharData(defaultType):
    typeBook = []
    for i in bookList:
        if defaultType == i.tag:
            typeBook.append(i)
    xData = ['小于500', '小于1000', '小于1500页', '小于2000页', '小于10000页', '10000页以上']
    yData = [0] * len(xData)  # 初始化yData为0，确保索引范围正确
    for i in typeBook:
        if int(i.comment_len) < 500:
            yData[0] += 1
        elif int(i.comment_len) < 1000:
            yData[1] += 1
        elif int(i.comment_len) < 1500:
            yData[2] += 1
        elif int(i.comment_len) < 2000:
            yData[3] += 1
        elif int(i.comment_len) < 10000:
            yData[4] += 1
        else:
            yData[5] += 1  # 10000页以上

    # 输出统计结果并返回
    print(yData)
    return xData, yData


def getCommentStar(defaultType):
    typeBook = []

    for i in bookList:
        if defaultType == i.tag:
            typeBook.append(i)

    xData = ['小于10', '小于20', '小于50', '小于100', '100以上']
    yData = [0] * len(xData)
    yData1 = [0] * len(xData)
    yData2 = [0] * len(xData)
    yData3 = [0] * len(xData)
    yData4 = [0] * len(xData)
    yData5 = [0] * len(xData)

    for i in typeBook:
        comments = json.loads(i.commentList)
        for j in comments:
            content_length = len(j['content'])
            if content_length < 10:
                yData[0] += 1
            elif content_length < 20:
                yData[1] += 1
            elif content_length < 50:
                yData[2] += 1
            elif content_length < 100:
                yData[3] += 1
            else:
                yData[4] += 1  # 100页以上

            # 检查是否存在 'start' 键
            # 星
            star = j.get('star', None)
            if star == 1:
                if content_length < 10:
                    yData1[0] += 1
                elif content_length < 20:
                    yData1[1] += 1
                elif content_length < 50:
                    yData1[2] += 1
                elif content_length < 100:
                    yData1[3] += 1
                else:
                    yData1[4] += 1
            if star == 2:
                if content_length < 10:
                    yData2[0] += 1
                elif content_length < 20:
                    yData2[1] += 1
                elif content_length < 50:
                    yData2[2] += 1
                elif content_length < 100:
                    yData2[3] += 1
                else:
                    yData2[4] += 1
            if star == 3:
                if content_length < 10:
                    yData3[0] += 1
                elif content_length < 20:
                    yData3[1] += 1
                elif content_length < 50:
                    yData3[2] += 1
                elif content_length < 100:
                    yData3[3] += 1
                else:
                    yData3[4] += 1
            if star == 4:
                if content_length < 10:
                    yData4[0] += 1
                elif content_length < 20:
                    yData4[1] += 1
                elif content_length < 50:
                    yData4[2] += 1
                elif content_length < 100:
                    yData4[3] += 1
                else:
                    yData4[4] += 1
            if star == 5:
                if content_length < 10:
                    yData5[0] += 1
                elif content_length < 20:
                    yData5[1] += 1
                elif content_length < 50:
                    yData5[2] += 1
                elif content_length < 100:
                    yData5[3] += 1
                else:
                    yData5[4] += 1

    print(yData)
    print(yData1)
    print(yData2)
    print(yData3)
    print(yData4)
    print(yData5)
    pieData = []
    pieData1 = []
    pieData2 = []
    pieData3 = []
    pieData4 = []
    pieData5 = []

    for index, value in enumerate(xData):
        pieData.append({
            'name': value,
            'value': yData[index]
        })
    for index, value in enumerate(xData):
        pieData1.append({
            'name': value,
            'value': yData1[index]
        })
    for index, value in enumerate(xData):
        pieData2.append({
            'name': value,
            'value': yData2[index]
        })
    for index, value in enumerate(xData):
        pieData3.append({
            'name': value,
            'value': yData3[index]
        })
    for index, value in enumerate(xData):
        pieData4.append({
            'name': value,
            'value': yData4[index]
        })
    for index, value in enumerate(xData):
        pieData5.append({
            'name': value,
            'value': yData5[index]
        })
    print(pieData)
    print(pieData3)
    return pieData, pieData1, pieData2, pieData3, pieData4, pieData5


def getYearBook():
    yearData = {}
    for i in bookList:
        if yearData.get(i.year[:4], -1) == -1:
            yearData[i.year[:4]] = 1
        else:
            yearData[i.year[:4]] += 1
    rateData = {}
    for key, value in yearData.items():
        if rateData.get(key, -1) == -1:
            rateData[key] = []

    for i in bookList:
        for key, value in rateData.items():
            if i.year[:4] == key:
                value.append(float(i.rate))
    for key, value in rateData.items():
        sum=0
        for item in value:
            sum += item
        rateData[key] = round(sum / len(value),1)

    print(rateData,yearData)
    return list(yearData.keys()), list(yearData.values()),list(rateData.values())

