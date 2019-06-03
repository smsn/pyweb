import os
import json
import asyncio
import inspect
import logging
from urllib import parse
from aiohttp import web
from jinja2 import FileSystemLoader
import aiohttp_jinja2
import time
from datetime import datetime
from api import APIError
from handlers import _COOKIE_NAME, cookie2user


class ParameterInspect(object):
    # https://docs.python.org/zh-cn/3/library/inspect.html
    def __init__(self, func):
        self.func = func
        self.sig = inspect.signature(func)
        self.params = self.sig.parameters
        self.has_request_arg = self._has_request_arg()  # request参数
        self.has_var_kw_arg = self._has_var_kw_arg()  # **kwargs
        self.get_required_kw_args = self._get_required_kw_args()  # *或*args 之后不带默认值的命名关键字参数
        self.get_name_kw_args = self._get_name_kw_args()  # *或*args 之后的命名关键字参数
        self.has_name_kw_args = True if self.get_name_kw_args else False  # *或*args 之后的命名关键字参数

    def _get_required_kw_args(self):
        args = []
        for name, param in self.params.items():
            if (param.kind == param.KEYWORD_ONLY and param.default is param.empty):
                # 值必须作为关键字参数提供。仅关键字参数是出现在 *或*args 之后的命名关键字参数
                # 不带默认值的参数
                args.append(name)
        return tuple(args)

    def _get_name_kw_args(self):
        args = []
        for name, param in self.params.items():
            if (param.kind == param.KEYWORD_ONLY):
                # 值必须作为关键字参数提供。仅关键字参数是出现在 *或*args 之后的命名关键字参数
                args.append(name)
        return tuple(args)

    def _has_var_kw_arg(self):
        for _, param in self.params.items():
            if (param.kind == param.VAR_KEYWORD):
                # 关键字参数的字典，未绑定到任何其他参数。这对应 **kwargs 中的参数
                return True

    def _has_request_arg(self):
        found = False
        for name, param in self.params.items():
            if name == 'request':
                found = True
                continue
            # 如果发现 request 后的下一个参数不是 **, *, *之后的参数
            # 说明request参数不是最后一个命名参数
            if found and (param.kind != param.VAR_KEYWORD and param.kind != param.VAR_POSITIONAL):
                raise ValueError("request parameter must be the last named parameter in function: {} .{}".format(self.func, str(self.sig)))
        return found


class RequestHandler(object):
    def __init__(self, app, func):
        _pi = ParameterInspect(func)
        self.app = app
        self.func = func
        self.func_name = func.__name__
        self.get_required_kw_args = _pi.get_required_kw_args  # *或*args 之后不带默认值的命名关键字参数
        self.get_name_kw_args = _pi.get_name_kw_args  # *或*args 之后的命名关键字参数
        self.has_name_kw_args = _pi.has_name_kw_args  # *或*args 之后的命名关键字参数
        self.has_var_kw_arg = _pi.has_var_kw_arg  # **kwargs
        self.has_request_arg = _pi.has_request_arg  # request参数

    async def _handler(self, request):
        # 当有请求时, 从`request`中获取必要的参数, 调用URL函数
        kw = None
        # 如果需要参数
        if self.has_var_kw_arg or self.has_name_kw_args:
            # 有 **kw 或 命名关键字参数
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest(text='No content_type.')
                content_type = request.content_type.lower()
                if content_type.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest(text='Body must be json.')
                    kw = params
                elif content_type.startswith('application/x-www-form-urlencoded') or content_type.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest(text='Unsupported Content-Type: {}.'.format(request.content_type))
            if request.method == 'GET':
                query_string = request.query_string
                if query_string:
                    kw = dict()
                    for k, v in parse.parse_qs(query_string, True).items():
                        kw[k] = v[0]
        # 不需要参数 或 没有取到参数
        if kw is None:
            kw = dict(**request.match_info)
        else:
            # 取到参数 且没有 **kw
            if not self.has_var_kw_arg:
                copy = dict()
                # 只取出需要的参数
                for name in self.get_name_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # 把request的信息添加到kw
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name {}:{} --> {}.'.format(k, kw[k], v))
                kw[k] = v
        if self.has_request_arg:
            kw['request'] = request
        # 如果存在没有默认值的必需参数
        # if self.get_required_kw_args:
        for name in self.get_required_kw_args:
            if name not in kw:
                return web.HTTPBadRequest(text='Missing argument: {}.'.format(name))
        logging.debug("[RequestHandler]:get response by: {}({})".format(self.func_name, str(kw)))
        try:
            rs = await self.func(**kw)
            return rs
        except APIError as e:
            return dict(error_type=e.error_type, error_kw=e.error_kw, message=e.message)

    def __call__(self, request):
        return self._handler(request)


async def logger_factory(app, handler):
    async def logger(request):
        logging.info("({}, {}) request start handler by: {}.".format(
            request.method, request.path, handler))
        rs = await handler(request)  # handler 是 request_factory.request_handler
        logging.info("({}, {}) request end.  --> ({}, {})".format(
            request.method, request.path, rs.status, rs.reason))
        return rs
    return logger  # middlewares 是 callable


async def request_factory(app, handler):
    async def request_handler(request):
        logging.debug("[request_factory]:request_handler start.")
        logging.debug("[request_factory]:handler cookie and get user.")
        cookie_str = request.cookies.get(_COOKIE_NAME)
        request.user = None
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.debug('get current user: {}'.format(user.email))
                request.user = user
        if request.path.startswith('/manage') and (request.user is None or not request.user.admin):
            return web.HTTPFound('/signin')
        logging.debug("[request_factory]:get response by: {}.".format(handler))
        rs = await handler(request)  # handler 是 response_factory.response_handler
        logging.debug("[request_factory]:get response ok.")
        return rs
    return request_handler


async def response_factory(app, handler):
    async def response_handler(request):
        logging.debug("[response_factory]:wait response body by {}".format(handler))
        rs = await handler(request)  # handler 是 hello: RequestHandler
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
            handler = RequestHandler(app, handler)
            logging.info("Add route {} {} --> {}{}".format(method, path, handler.func_name, handler.get_name_kw_args))
            app.router.add_route(method, path, handler)


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info("Add static {}".format(path))


def datetime_filter(created_at):
    _time = int(time.time() - created_at)
    if _time < 60:
        return '1分钟前'
    if _time < 3600:
        return '{}分钟前'.format(_time // 60)
    if _time < 86400:
        return '{}小时前'.format(_time // 3600)
    if _time < 604800:
        return '{}天前'.format(_time // 86400)
    dt = datetime.fromtimestamp(created_at)
    return '{}年{}月{}日'.format(dt.year, dt.month, dt.day)


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
    filters = kw.get('filters', None)
    if filters is not None:
        for name, func in filters.items():
            env.filters[name] = func
    app['__templating__'] = env
