from web_frame import get, post
from models import User, Blog, Comment


@get('/')
async def index(request):
    blogs = await Blog.find_all()
    return {"__template__": "blogs.html", "blogs": blogs}


@get(r'/test{tail:.*}')
async def test(request):
    # user6 = User(name='user6', email='user6@example.com', password='user6pass', avatar='about:blank')
    # await user6.save()  # user6.save() 仅仅是创建了一个协程, 要用await
    users_n = await User.find_count("name")
    print(users_n)
    users_1n = await User.find_count(where="id like ?", args=['30%'])
    print(users_1n)
    users = await User.find_all(where="id like ?", order_by="name desc", limit=(1, 3), args=["30%"])
    user = await User.find_by_pri_key(users[1].id)
    print(user)
    return {"__template__": "users.html", "users": users, "user": user}
