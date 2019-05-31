from models import User
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
    await orm.create_pool(user='pyweb', password='pyweb', db='pyweb_db', loop=loop)
    user1 = User(name='user1', email='user1@example.com', password='user1pass', avatar='about:blank')
    await user1.save()  # user1.save() 仅仅是创建了一个协程, 要用await
    # print(user1.id)
    # print(user1.get_value("id"))
    # print(user1.field_mappings)
    # print(user1.table_name)
    # print(user1["name"])
    # print(user1.name)
    print()
    user2 = User(name='user2', email='user2@example.com', password='user2pass', avatar='about:blank')
    await user2.save()
    print()
    user2.password = 'user222pass'
    user2.name = "user222"
    user2.avatar = "image"
    print()
    await user2.update()
    print()
    await user2.remove()
    print(dir(user1))
    print()
    print(dir(User))


async def test_find(loop):
    await orm.create_pool(user='pyweb', password='pyweb', db='pyweb_db', loop=loop)
    # user2 = User(name='user2', email='user2@example.com', password='user2pass', avatar='about:blank')
    # 使用元类创建User类,以避免需要在实例初始化时修改User类
    rs1 = await User.find_by_pri_key("3000")
    print(rs1)
    rs2 = await User.find_by_where("`id` like ?", ["30%"])
    print(rs2)


if __name__ == "__main__":
    # test_field()
    # test_obj()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_find(loop))
    loop.run_forever()
