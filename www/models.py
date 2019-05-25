from orm import Model, Field


def next_id():
    return 1


class User(Model):
    # 定义User类属性,实例属性通过__init__()方法初始化
    # 继承Model类方法，CURD 创建（Create）、更新（Update）、读取（Retrieve）和删除（Delete）
    # 定义 users 表字段 Field
    __table__ = 'users'
    id = next_id()
    email = ""
    password = ""
    admin = False
    name = "test"
    created_at = ""
    avatar = "image"


class Blog(Model):
    pass


print("start")

user = User(id=12345, name='Michael', email='test@orm.org', password='my-pwd')
print(user)
print(user.id)  # =User.id
print(user["id"])
print(user.avatar)
print()
