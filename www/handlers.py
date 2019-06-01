from web_frame import get, post
from models import User, Blog, Comment


@get('/')
async def index(request):
    blogs = await Blog.find_all()
    return {"__template__": "blogs.html", "blogs": blogs}


@get(r'/user{tail:.*}')
async def test(request):
    # user6 = User(name='user6', email='user6@example.com', password='user6pass', avatar='about:blank')
    # await user6.save()  # user6.save() 仅仅是创建了一个协程, 要用await
    users = await User.find_all()
    user = users[0]
    return {"__template__": "users.html", "users": users, "user": user}
