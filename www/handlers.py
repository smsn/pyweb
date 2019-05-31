from web_frame import get, post
from models import User


@get('/')
async def hello(request):
    user6 = User(name='user6', email='user6@example.com', password='user6pass', avatar='about:blank')
    await user6.save()
    users = await User.find_all()
    print(users[0])
    return {"__template__": "test.html", "users": users}


@get(r'/user{tail:.*}')
async def test(request):
    return (403, "test666")
