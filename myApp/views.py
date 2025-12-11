from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from myApp.models import *
from utils.getPublicData import *
from utils.getCharData import *
from model.index import *
import random


# Create your views here.

def home(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    print(userInfo, uname)
    userLen, typeLen, maxPrice, maxPriceBookName, maxRate, maxPageNum, rateList, rateListNum, createUserList, commentList = getHomeDataPage()
    return render(request, 'index.html', {
        'userInfo': userInfo,
        'userLen': userLen,
        'typeLen': typeLen,
        'maxPrice': maxPrice,
        'maxPriceBookName': maxPriceBookName,
        'maxRate': maxRate,
        'maxPageNum': maxPageNum,
        'rateList': rateList,
        'rateListNum': rateListNum,
        'createUserList': createUserList,
        'commentList': commentList[:20],

    })

#密码修改成功后返回登录页面，否则留在此页面
from django.shortcuts import redirect

def selfInfo(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)

    if request.method == 'POST':
        res = changePassword(uname, request.POST)

        if res is not None:
            if res == '密码修改成功':
                messages.success(request, res)  # 成功消息
                request.session.flush()  # 清除用户 session（强制重新登录）
                return redirect('/myApp/login/')  # **重定向到登录页面**
            else:
                messages.error(request, res)  # 失败消息
                return redirect('/myApp/selfInfo/')  # **返回个人信息页面**

    return render(request, 'selfInfo.html', {'userInfo': userInfo})

#密码修改成功后留在此页面

# def selfInfo(request):
#     uname = request.session.get('username')
#     userInfo = User.objects.get(username=uname)
#     print(userInfo, uname)
#     if request.method == 'POST':
#         print(request.POST)
#         res = changePassword(uname, request.POST)
#         if res is not None:
#             if res == '密码修改成功':
#                 messages.success(request, res)  # 使用 messages.success 显示成功消息
#
#             else:
#                 messages.error(request, res)  # 使用 messages.error 显示错误消息
#             return HttpResponseRedirect('/myApp/selfInfo/')
#     return render(request, 'selfInfo.html', {
#         'userInfo': userInfo,
#     })


def tableData(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    tableInfo = getTableData()

    return render(request, 'tableData.html', {
        'userInfo': userInfo,
        'tableInfo': tableInfo
    })


def typeChar(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    typeRes = getTypePieData()
    x1, y1, y2 = getTypeRateData()

    return render(request, 'typeChar.html', {
        'userInfo': userInfo,
        'typeRes': typeRes,
        'x1': x1,
        'y1': y1,
        'y2': y2

    })


def bookInfoChar(request):
    print(f"Session 数据: {request.session.items()}")  # 调试 Session
    uname = request.session.get('username')
    print(f"获取的用户名: {uname}")  # 添加这一行
    if not uname:
        print("用户未登录，重定向到登录页面")
        return redirect('/myApp/login/')
    try:
        userInfo = User.objects.get(username=uname)
    except User.DoesNotExist:
        print("用户不存在")
        return redirect('/myApp/login/')  # 如果用户不存在，重定向到登录页面

    # userInfo = User.objects.get(username=uname)
    typeList = getBookTypeList()
    defaultType = typeList[0]
    if request.GET.get('type'): defaultType = request.GET.get('type')
    xData, yData = getBookPriceData(defaultType)
    xData1, yData1 = getBookPageData(defaultType)

    print(defaultType)
    return render(request, 'bookInfoChar.html', {
        'userInfo': userInfo,
        'typeList': typeList,
        'defaultType': defaultType,
        'xData': xData,
        'yData': yData,
        'xData1': xData1,
        'yData1': yData1

    })


def commentChar(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    typeList = getBookTypeList()
    defaultType = typeList[0]
    if request.GET.get('type'): defaultType = request.GET.get('type')

    print(f"获取的用户名: {uname}")

    print(defaultType)
    xData, yData = getCommentLenCharData(defaultType)
    pieData, pieData1, pieData2, pieData3, pieData4, pieData5 = getCommentStar(defaultType)
    return render(request, 'commentChar.html', {
        'userInfo': userInfo,
        'typeList': typeList,
        'defaultType': defaultType,
        'xData': xData,
        'yData': yData,
        'pieData': pieData,
        'pieData1': pieData1,
        'pieData2': pieData2,
        'pieData3': pieData3,
        'pieData4': pieData4,
        'pieData5': pieData5

    })

def yearChar(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    x1,y1,y2=getYearBook()


    return render(request, 'yearChar.html', {
        'userInfo': userInfo,
        'x1':x1,
        'y1':y1,
        'y2':y2

    })

def titleCloud(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)

    return render(request, 'titleCloud.html', {
        'userInfo': userInfo,

    })

def summaryCloud(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)

    return render(request, 'summaryCloud.html', {
        'userInfo': userInfo,

    })


def recomBook(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    bookIdList=modelFn(int(userInfo.id))
    bookRes=[]
    for i in bookList:
        for j in bookIdList:
            if i.id==j:
                bookRes.append(i)
    print(len(bookRes))
    bookRes=bookRes[:30]
    bookRes=random.sample(bookRes,12)
    return render(request, 'recomBook.html', {
        'userInfo': userInfo,
        'bookRes': bookRes

    })

#已解决session丢失问题，即进行切换选择下拉框UserDoesNotExist问题
#也就是进行密码加密
from django.contrib.auth.hashers import check_password

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {})
    else:
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        print(uname, pwd)
        try:
            user = User.objects.get(username=uname)  # 只用 username 查询
            if check_password(pwd, user.password):  # 用 check_password 验证密码
                request.session['username'] = uname
                print(user)
                return redirect('/myApp/home/')
            else:
                messages.error(request, '用户名或密码错误')
                return redirect('/myApp/login/')
        except User.DoesNotExist:
            messages.error(request, '用户名或密码错误')
            return redirect('/myApp/login/')


#未解决session丢失问题，即进行切换选择下拉框UserDoesNotExist问题

# def login(request):
#     if request.method == 'GET':
#         return render(request, 'login.html', {})
#     else:
#         uname = request.POST.get('username')
#         pwd = request.POST.get('password')
#         print(uname, pwd)
#         try:
#             user = User.objects.get(username=uname, password=pwd)
#             request.session['username'] = uname
#             print(user)
#             return redirect('/myApp/home/')
#         except:
#             messages.error(request, '用户名或密码错误')
#             return HttpResponseRedirect('/myApp/login/')


def logOut(request):
    request.session.clear()
    return redirect('login')

from django.contrib.auth.hashers import make_password
# from myApp.models import User

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {})
    else:
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        rePwd = request.POST.get('checkPassword')
        print(uname, pwd, rePwd)
        message = ''

        try:
            # 检查用户是否存在
            User.objects.get(username=uname)
            message = '账号已经存在'
            messages.error(request, message)
            return HttpResponseRedirect('/myApp/register/')
        except User.DoesNotExist:
            if not uname or not pwd or not rePwd:
                message = '不允许为空'
                messages.error(request, message)
                return HttpResponseRedirect('/myApp/register/')
            elif pwd != rePwd:
                message = '两次密码不一致'
                messages.error(request, message)
                return HttpResponseRedirect('/myApp/register/')
            else:
                # 使用 make_password 来加密密码
                encrypted_password = make_password(pwd)
                user = User.objects.create(username=uname, password=encrypted_password)
                user.save()

                # 用户注册成功后可以选择自动登录或跳转到登录页
                messages.success(request, '注册成功，请登录！')
                return HttpResponseRedirect('/myApp/login/')  # 或者其他你希望跳转的页面

        return render(request, 'login.html', {})

