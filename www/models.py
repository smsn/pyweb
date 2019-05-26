from orm import Model, Field
import time
import uuid


def next_id():
    return "%015d%s000" % (int(time.time() * 1000), uuid.uuid4().hex)
    # "%015d"的意思：0代表不足位数的补0，这样可以确保相同的位数，15是位数也就是要得到到的字符串长度是15，d代表数字。


def bool_false():
    return False


class User(Model):
    # 定义User类属性, 映射 users 表字段 Field, 为实例添加默认函数
    # 实例属性通过__init__()方法初始化
    # 继承Model类方法，CURD 创建（Create）、更新（Update）、读取（Retrieve）和删除（Delete）
    # (field_name=None, field_type='varchar(100)', primary_key=False, default=None):
    __table__ = 'users'
    id = Field(field_type="varchar(50)", primary_key=True, default=next_id)
    email = Field(field_type="varchar(50)")
    password = Field(field_type="varchar(50)")
    admin = Field(field_type="boolean", default=bool_false)
    name = Field(field_type="varchar(50)")
    avatar = Field(field_type="varchar(500)")
    created_at = Field(field_type="real", default=time.time)


class Blog(Model):
    __table__ = 'blogs'
    id = Field(field_type="varchar(50)", primary_key=True, default=next_id)
    user_id = Field(field_type="varchar(50)")
    user_name = Field(field_type="varchar(50)")
    user_avatar = Field(field_type="varchar(500)")
    title = Field(field_type="varchar(50)")
    summary = Field(field_type="varchar(200)")
    content = Field(field_type="text")
    created_at = Field(field_type="real", default=time.time)


class Comment(Model):
    __table__ = 'comments'
    id = Field(field_type="varchar(50)", primary_key=True, default=next_id)
    blog_id = Field(field_type="varchar(50)")
    user_id = Field(field_type="varchar(50)")
    user_name = Field(field_type="varchar(50)")
    user_avatar = Field(field_type="varchar(500)")
    content = Field(field_type="text")
    created_at = Field(field_type="real", default=time.time)
