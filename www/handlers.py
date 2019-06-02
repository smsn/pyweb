from web_frame import get, post
from models import User, Blog, Comment


@get('/')
async def index(request):
    blogs = await Blog.find_all()
    return {"__template__": "blogs.html", "blogs": blogs}


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
