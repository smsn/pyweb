import asyncio
import logging
import aiomysql


async def create_pool(loop, **kwargs):
    # 创建连接池
    # **kwargs 关键字参数 city='Beijing' kwargs={'city': 'Beijing'}
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
    logging.info('SQL: {}\n     Args: {}'.format(sql, args))
    # 使用async with 自动关闭
    #   await cursor.close()
    #   conn.close()
    async with __pool.acquire() as conn:  # 创建连接 conn=await aiomysql.connect()
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 创建游标对象 cursor=await conn.cursor()
            # DictCursor 将结果作为字典返回的游标
            await cur.execute(sql.replace('?', '%s'), args or ())  # 执行
            #   query（str） - sql语句
            #   args（list） - sql查询的元组或参数列表
            if size:
                results = await cur.fetchmany(size)
            else:
                results = await cur.fetchall()
        logging.info('rows returned: %s' % len(results))
        return results  # 没有 conn.close() 连接复用


async def execute(sql, args, autocommit=True):
    # Insert, Update, Delete
    logging.info('SQL: {}\n     Args: {}'.format(sql, args))
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


class Model(object):
    pass
