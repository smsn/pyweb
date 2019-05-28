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


async def select(sql, args=(), size=None):
    # 查询
    logging.info('SQL: {}\n\tArgs: {}'.format(sql, args))
    # 使用async with 自动关闭
    #    await cursor.close()
    #    conn.close()
    async with __pool.acquire() as conn:  # 创建连接 conn=await aiomysql.connect()
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 创建游标对象 cursor=await conn.cursor() , DictCursor 将结果作为字典返回的游标
            await cur.execute(sql.replace('?', '%s'), args)  # 执行 cursor.execute("SELECT * FROM t1 WHERE id=%s", (5,))
            if size:
                results = await cur.fetchmany(size)
            else:
                results = await cur.fetchall()
        logging.info('rows returned: %s' % len(results))
        return results  # 没有 conn.close() 连接复用


async def execute(sql, args=(), autocommit=True):
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


class ModelMetaclass(type):
    def __new__(cls, name, bases, kwds):
        logging.info("\n使用 {} 创建 {} 类, 继承自{}\nkwds:{}\n".format(cls, name, bases, kwds))
        if "Model" == name:
            return type.__new__(cls, name, bases, kwds)
        table_name = kwds.get("table_name", name)
        table_fields = []
        field_mappings = {}
        primary_key_field = None
        for key, value in kwds.items():
            if isinstance(value, Field):
                table_fields.append(key)
                field_mappings[key] = value
                if value.primary_key:
                    if primary_key_field:
                        raise Exception("Duplicate primary key for field: {} | {}".format(
                            key, primary_key_field))
                    primary_key_field = key
        if not primary_key_field:
            raise Exception('Primary key not found.')
        for key in table_fields:
            kwds.pop(key)
        kwds["table_name"] = table_name
        kwds["table_fields"] = table_fields
        kwds["field_mappings"] = field_mappings
        kwds["primary_key_field"] = primary_key_field
        return type.__new__(cls, name, bases, kwds)


class Model(dict, metaclass=ModelMetaclass):
    # def __new__(cls, **kw):  # 使用元类 此处删除
    #     if not hasattr(cls, "table_fields"):  # 如果存在 'table_fields' 属性返回 True
    #         # 第一次处理父类时执行, 后续实例跳过
    #         # 对每一个实例都会重复执行 , 使用元类处理父类
    #         logging.info("处理 {} 类".format(cls.__name__))
    #         cls.table_fields = []
    #         cls.field_mappings = {}
    #         cls.primary_key_field = None
    #         cls.table_name = getattr(cls, "table_name", cls.__name__)
    #         for key, value in cls.__dict__.items():  # lll = dir(cls)
    #             if isinstance(value, Field):
    #                 if value.primary_key:
    #                     cls.primary_key_field = key
    #                 cls.table_fields.append(key)
    #                 cls.field_mappings[key] = value
    #         if not cls.primary_key_field:
    #             raise Exception('Primary key not found.')
    #         for key in cls.table_fields:
    #             delattr(cls, key)  # 删除属性 继承的父类属性无法删除
    #     return super().__new__(cls, **kw)

    def __init__(self, **kw):
        logging.info("初始化 {} 类, 创建实例\n{}\n".format(self.__class__.__name__, kw))
        super(Model, self).__init__(**kw)  # 调用父类 dict 的__init__方法, 添加 kw

    def __getattr__(self, key):
        # user.id 类属性
        # user[id] 字典
        # 当使用 user.id 时会访问类属性id，id不存在才会调用__getattr__，所以与 user[id] 不同
        try:
            # return self.get_value(key)
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        # 当__setattr__存在时，对 user.id 赋值不会修改类属性
        self[key] = value

    def get_value(self, key):
        value = getattr(self, key, "not exist")  # 访问对象的属性 key
        if "not exist" == value:  # 不存在则调用默认函数生成
            value = self.field_mappings[key].default
            if callable(value):
                value = value()
            setattr(self, key, value)
        return value

    def create_args(self):
        escaped_field = []
        args = []
        for key in self.table_fields:
            escaped_field.append("`%s`" % key)
            args.append(self.get_value(key))  # 获取实例属性值
        return args, escaped_field

    def create_args_string(self):
        args_string = ",%s" * len(self.table_fields)
        return args_string[1:]

    async def save(self):
        # 'insert into users (`email`,`password`,`id`) values (%s,%s,%s)', ("user3@mail","passwd",3000)
        args, escaped_field = self.create_args()
        # escaped_field = ",".join(map(lambda f: "`%s`"%f, self.table_fields))
        sql = "insert into `{}` ({}) values ({})".format(
            self.table_name,
            ",".join(escaped_field),
            self.create_args_string())
        await execute(sql, args)

    async def update(self):
        # update users set name='aaa',id="2000" where id=2000
        args, escaped_field = self.create_args()
        sql = "update `{}` set {} where `{}`={}".format(
            self.table_name,
            ",".join(map(lambda f: '%s=?'%f, escaped_field)),
            self.primary_key_field,
            self.get_value(self.primary_key_field))
        await execute(sql, args)

    async def remove(self):
        # 'delete from `users` where `id`=?'
        sql = "delete from `{}` where `{}`={}".format(
            self.table_name,
            self.primary_key_field,
            self.get_value(self.primary_key_field))
        await execute(sql)

    @classmethod
    async def find_by_pri_key(cls, pri_key):
        # 'select * from users where `id`=user_id
        sql = "select * from `{}` where `{}`={}".format(
            cls.table_name,
            cls.primary_key_field,
            pri_key)
        result = await select(sql)
        if len(result) == 0:
            return None
        return result[0]

    @classmethod
    async def find_by_where(cls, where, args=()):
        # select * from users where `name` like "user%";
        # select * from users where `name`="user1";
        sql = "select * from `{}` where {}".format(cls.table_name, where)
        result = await select(sql, args)
        return result
