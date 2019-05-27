drop database if exists pyweb_db;
create database pyweb_db;
use pyweb_db;

-- CREATE USER "pyweb"@"%" IDENTIFIED BY "pyweb";
grant all on pyweb_db.* to "pyweb"@"%" IDENTIFIED BY "pyweb";

create table users (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `password` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `avatar` varchar(500) not null,
    `created_at` real not null,
    unique key `idx_email` (`email`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_avatar` varchar(500) not null,
    `title` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_avatar` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;






-- >>> import pymysql
-- >>> mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'pyweb', password='pyweb', db= 'pyweb_db', cursorclass=pymysql.cursors.DictCursor)
-- >>> cur=mysql_conn.cursor()

-- >>> cur.execute('insert into users values (1000,"admin@mail","passwd","admin","img_url",1,444555666)')
-- >>> mysql_conn.commit()

-- >>> cur.execute('insert into users (`email`,`password`,`name`,`avatar`,`admin`,`created_at`,`id`) values ("user1@mail","passwd","user1","img_url",0,444555666,2000)')
-- >>> mysql_conn.commit()

-- >>> cur.execute('insert into users (`email`,`password`,`name`,`avatar`,`admin`,`created_at`,`id`) values (%s,%s,%s,%s,%s,%s,%s)', ("user3@mail","passwd","user3","img_url",0,444555666,3000))
-- >>> mysql_conn.commit()

-- >>> cur.execute('update users set name='aaa' where id=2000')
-- >>> cur.execute('delete from where id=2000')

-- >>> cur.execute('SELECT * from users')
-- >>> cur.fetchone()
-- >>> cur.fetchall()

