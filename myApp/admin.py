from django.contrib import admin
from myApp.models import *

class DbBooks(admin.ModelAdmin):
    list_display=["id","bookId","tag","title","cover","author","press","year","pageNum","price","rate","starList","createTime",]
    list_display_links=["title"]
    list_filter=["tag"]
    search_fields=["title","author","press"]
    list_editable = ["cover"]
    readonly_fields = ["id"]
    list_per_page = 15


admin.site.register(BookList,DbBooks)

class UserA(admin.ModelAdmin):
    list_display=["id","username","password","createTime"]
    list_display_links=["username"]
    search_fields = ["username"]
    readonly_fields = ["id"]
    list_per_page = 15
    date_hierarchy = "createTime"

admin.site.register(User,UserA)

# Register your models here.
admin.site.site_header = '豆瓣图书数据管理'
admin.site.site_title = '豆瓣图书数据管理'
