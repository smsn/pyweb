# Python Web 异步Blog


参考[实战 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1016959663602400/1018138095494592)


>关键词`ORM`, `Model`, `异步`, `基于生成器的协程`, `MySQL`, `aiohttp`, `基于Socket的Web服务器`, `Web框架`, `MVC`


## 实现功能
* [截图](screenshots/README.md)
* `GET ('/')`  首页
* `GET ('/register')`  注册页面
* `POST('/api/register')`  注册API
* `GET ('/signin')`  登录页面
* `POST('/api/signin')`  登录API
* `GET ('/signout')`  退出登录
* `GET ('/admin/users')`  管理users页面
* `GET ('/api/users')`  获取用户列表 API
* `GET ('/admin/blogs')`  管理blogs页面
* `GET ('/api/blogs')`  获取blog列表 API
* `GET ('/blog/{blog_id}')`  获取blog页面
* `GET ('/api/blog/{blog_id}')`  获取blog API
* `GET ('/create/blog')`  创建blog页面
* `POST('/api/create/blog')`  创建blog API
* `POST('/api/blog/{blog_id}/update')`  更新blog API
* `POST('/api/blog/{blog_id}/delete')`  删除blog API
* `GET ('/api/blog/{blog_id}/comments')`  获取某blog评论 API
* `POST('/api/blog/{blog_id}/comments')`  创建某blog评论 API
* `POST('/api/comment/{comment_id}/delete')`  删除评论 API


## 运行
1. 导入`schema.sql`
2. `python app.py`
3. 访问`http://0.0.0.0:8080/`
