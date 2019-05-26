import asyncio
import aiomysql
import logging
logging.basicConfig(level=logging.INFO)


async def create_pool(loop, **kwargs):
    # 创建连接池
    # **kwargs 关键字参数 eg:city='Beijing'  kwargs={'city': 'Beijing'}
    logging.info("create database connection pool ...")
    global __pool
    __pool = await aiomysql.create_pool(
        host=kwargs.get("host", "localhost"),  # 默认localhost
        port=kwargs.get("port", 3306),
        user=kwargs["user"],
        password=kwargs["password"],
        db=kwargs["db"],
        autocommit=True,  # 提交事务 更改数据库 conn.commit()
        loop=loop,
    )


async def select(sql, args, size=None):
    # 查询
    logging.info('SQL: {}\n\tArgs: {}'.format(sql, args))
    # 使用async with 自动关闭
    #    await cursor.close()
    #    conn.close()
    async with __pool.acquire() as conn:  # 创建连接 conn=await aiomysql.connect()
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 创建游标对象 cursor=await conn.cursor() , DictCursor 将结果作为字典返回的游标
            await cur.execute(sql.replace('?', '%s'), args or ())  # 执行 cursor.execute("SELECT * FROM t1 WHERE id=%s", (5,))
            if size:
                results = await cur.fetchmany(size)
            else:
                results = await cur.fetchall()
        logging.info('rows returned: %s' % len(results))
        return results  # 没有 conn.close() 连接复用


async def execute(sql, args, autocommit=True):
    # Insert, Update, Delete
    logging.info('\nSQL: {}\nArgs: {}\n'.format(sql, args))
    async with __pool.acquire() as conn:
        if not autocommit:
            await conn.begin()  # 开始事务  A coroutine to begin transaction.
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount  # 受影响的行数
            if not autocommit:
                await conn.commit()  # 提交事务
        except BaseException as e:
            logging.warning("execute fail: {}".format(e))
            if not autocommit:
                await conn.rollback()  # 回滚 原子性（Atomicity）
            raise
        return affected


class Field(object):
    #  Field | Type | Null | Key | Default | Extra
    def __init__(self, field_name=None, field_type='varchar(100)', primary_key=False, default=None):
        self.field_name = field_name
        self.field_type = field_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        # obj.__str__() 方法会在 print(obj) 或 '{}'.format(obj) 时被调用
        # __repr__()用于显示给开发人员, eg: <main.Person object at 0x10c941890>
        return "{}:{} | {} | {}".format(self.__class__.__name__, self.field_type, self.primary_key, self.default)


class Model(dict):
    def __init__(self, **kw):
        logging.info("初始化 {} 类, 创建实例\nattrs:{}\n".format(self.__class__.__name__, kw))
        # self.__fields__ = []
        # self.__mappings__ = {}  # 会调用 __setattr__()
        self["__fields__"] = []
        self["__mappings__"] = {}
        for k, v in self.__class__.__dict__.items():
            # {'__module__': 'models', '__table__': 'users', 'id': <orm.Field object at 0x7f90ff23ef28>,}
            if isinstance(v, Field):
                # self.__fields__.append(k)
                # self.__mappings__[k] = v  # 保存表字段 , self.__mappings__ 会调用 __getattr__
                self["__mappings__"][k] = v  # 保存表字段
                self["__fields__"].append(k)
        for key in self["__fields__"]:
            # delattr(self, key)  # 删除实例属性
            print(key)
            setattr(self, key, kw[key])
        # super(Model, self).__init__(**kw)  # 调用父类 dict 的__init__方法, 添加 kw

    # def __getattr__(self, key):
    #     # user.id 类属性
    #     # user[id] 字典
    #     # 当使用 user.id 时会访问类属性id，id不存在才会调用__getattr__，所以与 user[id] 不同
    #     try:
    #         return self[key]
    #     except KeyError:
    #         raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    # def __setattr__(self, key, value):
    #     # 当__setattr__存在时，对 user.id 赋值不会修改类属性
    #     self[key] = value

    def get_value(self, key):
        value = getattr(self, key, None)  # 访问对象的属性 key
        # self[key], self["__mappings__"][key].default()
        return value

    def create_args(self):
        escaped_fields = []
        args = []
        for key in self["__fields__"]:
            escaped_fields.append("`%s`" % key)
            # 获取实例属性值, 不存在则调用默认函数生成
            args.append(self.get_value(key))
        # escaped_fields = ",".join(list(map(lambda f: "`%s`"%f, escaped_fields)))
        escaped_fields = ",".join(escaped_fields)
        return args, escaped_fields

    def create_args_string(self):
        args_string = ",%s" * len(self["__fields__"])
        return args_string[1:]

    async def save(self):
        # 'insert into users (`email`,`password`,`id`) values (%s,%s,%s)', ("user3@mail","passwd",3000)
        args, escaped_fields = self.create_args()
        sql = "insert into `{}` ({}) values ({})".format(self.__table__, escaped_fields, self.create_args_string())
        await execute(sql, args)

    def find(self):
        pass
