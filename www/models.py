from orm import Model


def next_id():
    return 1


class User(Model):
    # 定义User类属性,实例属性通过__init__()方法初始化
    # 继承Model类方法，CURD 创建（Create）、更新（Update）、读取（Retrieve）和删除（Delete）
    __table__ = 'users'
    id = next_id()
    email = ""
    password = ""
    admin = False
    name = ""
    avatar = ""
    created_at = ""


class Blog(Model):
    pass
