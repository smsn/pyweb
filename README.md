# learn python web

## asyncio
* https://docs.python.org/zh-cn/3/library/asyncio-llapi-index.html
* 深入理解Python异步编程
    - http://python.jobbole.com/88291/
* 使用`yield`, `yield from`, `回调`, `事件循环`, 实现一个异步爬虫(基于`生成器`的协程)

## orm
* 对象关系映射`Object Relational Mapping`
* 访问数据库需要创建数据库连接、游标对象, 然后执行SQL语句, 最后处理异常, 清理资源。
* 这些访问数据库的代码如果分散到各个函数中, 势必无法维护, 也不利于代码复用。
* 所以, 我们要首先把常用的`SELECT`、`INSERT`、`UPDATE`和`DELETE`操作用函数封装起来。

## mysql(mariadb)
* https://wiki.jikexueyuan.com/project/linux/mysql.html
* https://zh.wikipedia.org/zh-hans/数据库事务
+ 数据库事务(简称事务)是数据库管理系统执行过程中的一个逻辑单位, 由一个有限的数据库操作序列构成。
+ 原子性(Atomicity): 事务作为一个整体被执行, 包含在其中的对数据库的操作要么全部被执行, 要么都不执行(回滚)

## aiomysql
* https://aiomysql.readthedocs.io
* https://pymysql.readthedocs.io/en/latest/user/examples.html

## Python中的下划线和`special-method`
* `special-method`
    - https://docs.python.org/zh-cn/3/reference/datamodel.html?#special-method-names
* 单下划线(`_`)
    - 作为临时性的名称使用, 分配了一个特定的名称, 但是并不会在后面再次用到该名称, `for _ in range(n):`
* 名称前的单下划线(如:`_shahriar`)
    - "私有", 这有点类似于惯例, 为了使其他人(或你自己)使用这些代码时将会知道以"_"开头的名称只供内部使用
* 名称前的双下划线(如:`__shahriar`)
    - Python中的这种用法是为了避免与子类定义的名称冲突, 解释器会修改`__method_name`为`_ClassName__method_name`
* 名称前后的双下划线(如:`__init__`)
    - 这种用法表示Python中特殊的方法名, 通常你将会覆写这些方法, 并在里面实现你所需要的功能, 以便Python调用它们。例如, 当定义一个类时, 你经常会覆写`__init__`方法。

## 元类(metaclass)
* 理解为什么要使用元类, 解决了什么问题
    - 先不使用元类 --> 发现问题 --> 可以使用元类解决
* 作用: 定制类
    - 定义`metaclass`, 就可以对类加工修改, 创建符合要求的类。

## 函数注释(可选)
* https://www.python.org/dev/peps/pep-3107/
* 注释始终位于参数的默认值之前
```
    >>> def foobar(a: 1+1, b: "it's b", c: str = 5) -> tuple:
    ...     return a, b, c
    >>> foobar.__annotations__
    {'a': 2, 'b': "it's b", 'c': <class 'str'>, 'return': <class 'tuple'>}
    >>> foobar(1, 2)
    (1, 2, 5)
    >>> foobar(1, 2, 3)
    (1, 2, 3)
```

## 实现一个简单的web server
* http://python.jobbole.com/81820/?utm_source=blog.jobbole.com&utm_medium=relatedPosts

## 实现一个简单的web框架(WSGI, PEP333)
* https://dantangfan.github.io/2015/04/15/how-to-make-a-python-web-framework.html

## aiohttp
* 异步 HTTP 客户端和服务端
* https://aiohttp.readthedocs.io

## 实现一个简单的基于`aiohttp`的web框架
* 自动扫描`handlers.py`里的URL函数并添加路由
* `middlewares`: 中间件是可以修改请求或响应中的协程
    - https://aiohttp.readthedocs.io/en/stable/web_advanced.html#middlewares
    - 在内部, 通过以相反的顺序返回`RequestHandler(request)`的结果`response`, 当有请求`request`时, 执行情况如下:
```
    middlewares=[logger_factory, request_factory, response_factory]

    response_factory(app, hello) ->  response_handler
    request_factory(app, response_handler) -> request_handler
    logger_factory(app, request_handler) -> logger

    logger(request) -> ... -> await request_handler(request) -> ...
        request_handler(request) -> ... -> await response_handler(request) -> ...
            response_handler(request) -> ... -> await hello(request) -> ...
```
* `request_factory`: 在调用URL函数前可以拦截请求等
* `response_factory`: 构造`web.Response`
* `RequestHandler`: 分析URL函数需要接收的参数, 包装URL函数传递给路由, 当有请求时, 从`request`中获取必要的参数, 调用URL函数. 与`request_factory`分开是为了在初始化时检查参数错误.

## `inspect`模块, 函数参数分析
* https://docs.python.org/zh-cn/3/library/inspect.html

## Chromium
* 禁止缓存, 修改css等可立即生效
* DevTools --> Network --> Disable cache

## `REST(Representational State Transfer) API`
* 简单来说,就是看到请求 `GET /api/blog/id/123` 就知道要干什么