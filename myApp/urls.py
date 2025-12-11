from django.urls import path
from myApp import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("logOut/", views.logOut, name="logOut"),
    path("register/", views.register, name="register"),
    path("selfInfo/", views.selfInfo, name="selfInfo"),
    path("tableData/", views.tableData, name="tableData"),
    path("typeChar/", views.typeChar, name="typeChar"),
    path("bookInfoChar/", views.bookInfoChar, name="bookInfoChar"),
    path("commentChar/", views.commentChar, name="commentChar"),
    path("yearChar/", views.yearChar, name="yearChar"),
    path("titleCloud/", views.titleCloud, name="titleCloud"),
    path("summaryCloud/", views.summaryCloud, name="summaryCloud"),
    path("recomBook/", views.recomBook, name="recomBook"),

]
