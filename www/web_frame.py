import functools
import os
import json
import asyncio
import inspect
import logging
from aiohttp import web
from jinja2 import FileSystemLoader
import aiohttp_jinja2


async def logger_factory(app, handler):
    async def logger(request):
        logging.info("({}, {}) request start.".format(
            request.method, request.path))
        rs = await handler(request)  # handler 是 response_factory.response_handler
        logging.info("({}, {}) request end.  --> ({}, {})".format(
            request.method, request.path, rs.status, rs.reason))
        return rs
    return logger  # middlewares 是 callable


async def response_factory(app, handler):
    async def response_handler(request):
        logging.debug("[response_factory]:wait response body by {}".format(handler))
        rs = await handler(request)  # handler 是 request_factory.request_handler
        logging.debug("[response_factory]:make response body (type:{} | len:{})".format(type(rs), len(rs)))
        if isinstance(rs, web.StreamResponse):
            return rs
        if isinstance(rs, bytes):
            resp = web.Response(body=rs)
            resp.content_type = "application/octet-stream"
            return resp
        if isinstance(rs, str):
            if rs.startswith("redirect:"):
                return web.HTTPFound(rs[9:])
            resp = web.Response(body=rs.encode('utf-8'))
            resp.content_type = "text/html;charset=utf-8"
            return resp
        if isinstance(rs, dict):
            template = rs.get('__template__')
            if template is None:
                # ``default（obj）``是一个应该返回可序列化版本的函数obj或引发TypeError
                resp = web.Response(
                    body=json.dumps(rs, ensure_ascii=False, default=lambda x: x.__dict__).encode('utf-8'))
                resp.content_type = "application/json;charset=utf-8"
                return resp
            else:
                resp = web.Response(
                    body=app['__templating__'].get_template(template).render(**rs).encode('utf-8'))
                resp.content_type = "text/html;charset=utf-8"
                return resp
        if isinstance(rs, tuple) and len(rs) == 2:
            return web.Response(status=rs[0], reason=rs[1])
        resp = web.Response(body=str(rs).encode('utf-8'))
        resp.content_type = "text/plain;charset=utf-8"
        return resp
    return response_handler


async def request_factory(app, handler):
    async def request_handler(request):
        logging.debug("[request_factory]:request_handler start.")
        if request.method == 'GET':
            pass
        if request.method == 'POST':
            pass
        logging.debug("[request_factory]:get response by {}".format(handler))
        rs = await handler(request)  # handler 是 hello
        logging.debug("[request_factory]:get response ok.")
        return rs
    return request_handler


def get(path):
    def decorator(func):
        # functools.wraps 可以将原函数对象的指定属性复制给包装函数对象,
        # 默认有 __module__、__name__、__doc__
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.method = 'GET'
        wrapper.path = path
        return wrapper
    return decorator


def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.method = 'POST'
        wrapper.path = path
        return wrapper
    return decorator


def add_routes(app, module_name):
    mod = __import__(module_name)
    for attr in dir(mod):
        if attr.startswith("_"):
            continue
        handler = getattr(mod, attr)
        method = getattr(handler, 'method', None)
        path = getattr(handler, 'path', None)
        if method and path:
            # 如果函数即不是一个协程也不是生成器，那就把函数变成一个协程
            if not asyncio.iscoroutinefunction(handler) and not inspect.isgeneratorfunction(handler):
                handler = asyncio.coroutine(handler)
            app.router.add_route(method, path, handler)
            logging.info("Add route {} {}".format(method, path))


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info("Add static {}".format(path))


def init_jinja2(app, **kw):
    logging.info("Init jinja2 ...")
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True))
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = aiohttp_jinja2.setup(app, loader=FileSystemLoader(path), **options)
    app['__templating__'] = env