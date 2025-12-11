# 豆瓣图书系统ER图

```mermaid
erDiagram
    User ||--o{ UserBehavior : 产生
    BookList ||--o{ UserBehavior : 接收
    Admin ||--o{ BookList : 管理
    Admin ||--o{ User : 管理
    
    User {
        int id PK "用户ID"
        string username "用户名"
        string password "密码"
        datetime createTime "创建时间"
    }
    
    BookList {
        int id PK "图书ID"
        string bookId "书籍编号"
        string tag "类型"
        string title "书名"
        string cover "封面"
        string author "作者"
        string press "出版社"
        string year "出版年份"
        string pageNum "页码"
        string price "价格"
        string rate "评分"
        string starList "星级列表"
        text summary "描述"
        string detailLink "详情链接"
        string createTime "创建时间"
        string comment_len "评论数量"
        text commentList "评论列表"
    }
    
    UserBehavior {
        int id PK "行为ID"
        int user_id FK "用户ID"
        int book_id FK "图书ID"
        string behavior_type "行为类型"
        int rating "评分"
        datetime timestamp "行为时间"
    }
    
    Admin {
        int id PK "管理员ID"
        string username "用户名"
        string password "密码"
        string email "邮箱"
        datetime last_login "最后登录时间"
        boolean is_superuser "是否超级管理员"
        boolean is_staff "是否职员"
        boolean is_active "是否激活"
    }
```

## 实体说明

1. **User (用户)**
   - 普通用户实体，包含基本用户信息
   - 可以对图书进行浏览、评分、收藏等操作

2. **BookList (图书)**
   - 图书实体，包含图书的详细信息
   - 包括书籍基本信息、评分信息和评论信息

3. **UserBehavior (用户行为)**
   - 记录用户与图书之间的交互行为
   - 包括浏览、评分、收藏、点击等行为类型

4. **Admin (管理员)**
   - 系统管理员实体，负责管理系统
   - 具有对用户和图书的管理权限

## 关系说明

1. 用户可以对多本图书产生多种行为（一对多关系）
2. 图书可以被多个用户进行多种操作（一对多关系）
3. 管理员可以管理多个用户和多本图书（一对多关系）