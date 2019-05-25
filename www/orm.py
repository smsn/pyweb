import asyncio
import aiomysql
import logging
logging.basicConfig(level=logging.INFO)

async def create_pool(loop, **kwargs):
    # 创建连接池
    # **kwargs 关键字参数 eg:city='Beijing'  kwargs={'city': 'Beijing'}
    logging.debug("create database connection pool ...")
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
            # 创建游标对象 cursor=await conn.cursor()
            # DictCursor 将结果作为字典返回的游标
            await cur.execute(sql.replace('?', '%s'), args or ())  # 执行
            # cursor.execute("SELECT * FROM t1 WHERE id=%s", (5,))
            if size:
                results = await cur.fetchmany(size)
            else:
                results = await cur.fetchall()
        logging.info('rows returned: %s' % len(results))
        return results  # 没有 conn.close() 连接复用


async def execute(sql, args, autocommit=True):
    # Insert, Update, Delete
    logging.info('SQL: {}\n\tArgs: {}'.format(sql, args))
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
    def __init__(self,):
        pass


class Model(dict):
    def __init__(self, **kw):
        logging.info("初始化 {} 类, 创建实例\n\tattrs:{}\n".format(self.__class__.__name__, kw))
        super(Model, self).__init__(**kw)  # 调用父类 dict 的__init__方法
        self.fields = []
        for k in kw.keys():
            self.fields.append(k)

    def __getattr__(self, key):
        # user.id 类属性
        # user[id] 字典
        # 当使用 user.id 时会访问类属性id，id不存在才会调用__getattr__，所以与 user[id] 不同
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        # 当__setattr__存在时，对 user.id 赋值不会修改类属性
        self[key] = value

    async def save(self):
        # cur.execute('insert into users (`email`,`password`,`id`) values (%s,%s,%s)', ("user3@mail","passwd",3000))
        # await execute('insert into `%s` (%s) values (%s)', (self.__table__, Field.))
        pass

    def find(self):
        pass
