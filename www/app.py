LOG_FORMAT = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
import logging; logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

from aiohttp import web
import asyncio
import orm
from web_frame import (add_routes, add_static, init_jinja2, logger_factory,
                       request_factory, response_factory)


async def init(loop):
    await orm.create_pool(user='pyweb', password='pyweb', db='pyweb_db', loop=loop)
    app = web.Application(loop=loop, middlewares=[logger_factory, response_factory, request_factory])
    add_routes(app, 'handlers')
    add_static(app)
    init_jinja2(app)
    # 参数 app.make_handler() 返回一个可调用对象。下面是源码里的代码,定义了__call__,返回一个请求处理函数
    # def __call__(self) -> RequestHandler:
    #     return RequestHandler(self, loop=self._loop, **self._kwargs)
    server = await loop.create_server(app.make_handler(), host='0.0.0.0', port=8080)
    logging.info('Server started at http://0.0.0.0:8080 ...')
    return server

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
