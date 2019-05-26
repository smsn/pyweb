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
