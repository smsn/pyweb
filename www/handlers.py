import re
import time
import json
import hashlib
import logging
import functools
from aiohttp import web
from models import next_id, User, Blog, Comment
from api import APIError, APIValueError, APIResourceNotFoundError, APIPermissionError
from config import configs

_COOKIE_NAME = configs['session']['cookie_name']
_COOKIE_KEY = configs['session']['secret_key']
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


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


def get_page_index(page):
    try:
        p = int(page)
    except:
        p = 1
    if p < 1:
        p = 1
    return p


class Page(object):
    def __init__(self, total, page_index=1, page_size=10):
        self.total = total  # 总数
        self.page_size = page_size  # 每页数量
        self.page_count = total // page_size + (1 if total % page_size > 0 else 0)  # 总页数
        if (total == 0) or (page_index > self.page_count):
            self.start_index = 0
            self.limit_num = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.start_index = self.page_size * (page_index - 1)
            self.limit_num = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def __str__(self):
        return "total:{}, page_index:{}, page_size:{}, page_count:{}, start_index:{}, limit_num:{}, has_next:{}, has_previous:{}".format(self.total, self.page_index, self.page_size, self.page_count, self.start_index, self.limit_num, self.has_next, self.has_previous)

    __repr__ = __str__


def user2cookie(user, max_age):
    # "用户id" + "过期时间" + SHA1("用户id" + "用户口令" + "过期时间" + "SecretKey")
    expiration_date = str(int(time.time() + max_age))
    _s = "{}-{}-{}-{}".format(user.id, user.password, expiration_date, _COOKIE_KEY)
    _l = [user.id, expiration_date, hashlib.sha1(_s.encode('utf-8')).hexdigest()]
    return "-".join(_l)


async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        _l = cookie_str.split('-')
        if len(_l) != 3:
            return None
        user_id, expiration_date, sha1 = _l
        if int(expiration_date) < time.time():
            return None
        user = await User.find_by_pri_key(user_id)
        if user is None:
            return None
        _s = "{}-{}-{}-{}".format(user_id, user.password, expiration_date, _COOKIE_KEY)
        if sha1 != hashlib.sha1(_s.encode('utf-8')).hexdigest():
            return None
        user.password = '******'
        return user
    except Exception as e:
        logging.warning('cookie2user wrong: {}'.format(e))
        return None


@get('/')
async def index(request):
    blogs = await Blog.find_all()
    return {"__template__": "blogs.html", "blogs": blogs}


@get('/register')
async def register():
    return {"__template__": "register.html"}


@get('/signin')
async def signin():
    return {"__template__": "signin.html"}


@get('/signout')
async def signout(request):
    referer = request.headers.get("Referer")
    resp = web.HTTPFound(referer or '/')
    resp.set_cookie(_COOKIE_NAME, "-deleted-", max_age=0, httponly=True)
    return resp


@get('/api/users')
async def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    user_total = await User.find_count('id')
    _p = Page(user_total, page_index)
    if user_total == 0:
        return dict(msg='no data', page=_p, users=())
    users = await User.find_all(order_by='created_at desc', limit=(_p.start_index, _p.limit_num))
    for user in users:
        user.password = '******'
    return dict(msg='success', page=_p, users=users)


@post('/api/signin')
async def api_signin(*, email, password):
    if not email:
        raise APIValueError('email')
    if not password:
        raise APIValueError('password')
    user = await User.find_all(where='email=?', args=[email])
    if len(user) == 0:
        raise APIValueError('email', 'Email not exists.')
    user = user[0]
    sha1_password = hashlib.sha1('{}:{}'.format(user.id, password).encode('utf-8')).hexdigest()
    if user.password != sha1_password:
        raise APIValueError('password', 'Wrong password.')
    resp = web.Response()
    resp.set_cookie(_COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.password = '******'
    user.msg = 'signin success'
    resp.content_type = 'application/json'
    resp.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return resp


@post('/api/register')
async def api_register_user(*, email, name, password):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    # if not password or not _RE_SHA1.match(password):
    if not password:
        raise APIValueError('password')
    users = await User.find_count(where='email=?', args=[email])
    if users:
        raise APIError('register:failed', 'email', 'Email already exists.')
    user_id = next_id()
    # hexdigest()函数将hash对象转换成16进制表示的字符串
    sha1_password = hashlib.sha1('{}:{}'.format(user_id, password).encode('utf-8')).hexdigest()
    avatar = "http://www.gravatar.com/avatar/{}?d=mm&s=120".format(hashlib.md5(email.encode('utf-8')).hexdigest())
    user = User(id=user_id, name=name.strip(), email=email, password=sha1_password, avatar=avatar)
    await user.save()
    resp = web.Response()
    resp.set_cookie(_COOKIE_NAME, user2cookie(user, 600), max_age=600, httponly=True)
    user.password = '******'
    user.msg = 'register success'
    resp.content_type = 'application/json'
    resp.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return resp


@get(r'/test{tail:.*}')
async def test(request):
    # for i in range(200):
    #     user = User(name='user%d' % i, email='user%d@example.com' % i, password='user%dpass' % i, avatar='user%dimg' % i)
    #     await user.save()  # user6.save() 仅仅是创建了一个协程, 要用await
    users_n = await User.find_count("name")
    print(users_n)
    users_1n = await User.find_count(where="name like ?", args=['user10%'])
    print(users_1n)
    users = await User.find_all(order_by="name desc", limit=(1, 10))
    print(len(users))
    user = await User.find_by_pri_key(users[1].id)
    print(user)
    return {"__template__": "users.html", "users": users, "user": user}
