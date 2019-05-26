from models import User
# , Blog, Comment
import orm
import asyncio


def test_field():
    print("test_field ...")
    print(User)
    print(format("__table__:", " <11s"), User.__table__)
    print(format("", " <11s"), "Field | Type | Key | Default")
    print(format("id:", " <11s"), User.id)
    print(format("email:", " <11s"), User.email)
    print(format("password:", " <11s"), User.password)
    print(format("admin:", " <11s"), User.admin)
    print(format("name:", " <11s"), User.name)
    print(format("avatar:", " <11s"), User.avatar)
    print(format("created_at:", " <11s"), User.created_at)


async def test_obj(loop):
    user1 = User(name='user1', email='user1@example.com', password='user1pass', avatar='about:blank')
    print(user1.__table__)
    print(user1.name)
    print(user1["name"])
    print()
    await orm.create_pool(user='pyweb', password='pyweb', db='pyweb_db', loop=loop)
    await user1.save()  # user1.save() 仅仅是创建了一个协程, 要用await
    print()


if __name__ == "__main__":
    # test_field()
    # test_obj()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_obj(loop))
    loop.run_forever()
