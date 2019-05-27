# learn python web

## asyncio
* yield、回调、事件循环

## aiohttp
* 异步 HTTP 客户端和服务端

## orm
* 对象关系映射 Object Relational Mapping
* 访问数据库需要创建数据库连接、游标对象，然后执行SQL语句，最后处理异常，清理资源。
* 这些访问数据库的代码如果分散到各个函数中，势必无法维护，也不利于代码复用。
* 所以，我们要首先把常用的SELECT、INSERT、UPDATE和DELETE操作用函数封装起来。

## mysql
* https://wiki.jikexueyuan.com/project/linux/mysql.html
* https://zh.wikipedia.org/zh-hans/数据库事务

+ 数据库事务（简称：事务）是数据库管理系统执行过程中的一个逻辑单位，由一个有限的数据库操作序列构成。
+ 数据库事务通常包含了一个序列的对数据库的读/写操作。包含有以下两个目的：
    - 为数据库操作序列提供了一个从失败中恢复到正常状态的方法，同时提供了数据库即使在异常状态下仍能保持一致性的方法。
    - 当多个应用程序在并发访问数据库时，可以在这些应用程序之间提供一个隔离方法，以防止彼此的操作互相干扰。
+ 当事务被提交给了数据库管理系统（DBMS），则DBMS需要确保该事务中的所有操作都成功完成且其结果被永久保存在数据库中，如果事务中有的操作没有成功完成，则事务中的所有操作都需要回滚，回到事务执行前的状态；同时，该事务对数据库或者其他事务的执行无影响，所有的事务都好像在独立的运行。
+ 原子性（Atomicity）：事务作为一个整体被执行，包含在其中的对数据库的操作要么全部被执行，要么都不执行

## aiomysql
* https://aiomysql.readthedocs.io
* https://pymysql.readthedocs.io/en/latest/user/examples.html

## Python中的下划线
* 单下划线（_）
    - 作为临时性的名称使用,分配了一个特定的名称，但是并不会在后面再次用到该名称,for _ in range(n):
* 名称前的单下划线（如：_shahriar）
    - “私有”。这有点类似于惯例，为了使其他人（或你自己）使用这些代码时将会知道以“_”开头的名称只供内部使用
* 名称前的双下划线（如：__shahriar）
    - Python中的这种用法是为了避免与子类定义的名称冲突,解释器会修改“__method_name”为“_ClassName__method_name”
* 名称前后的双下划线（如：__init__）
    - 这种用法表示Python中特殊的方法名,通常，你将会覆写这些方法，并在里面实现你所需要的功能，以便Python调用它们。例如，当定义一个类时，你经常会覆写“__init__”方法。
    - https://docs.python.org/zh-cn/3/reference/datamodel.html?#special-method-names
