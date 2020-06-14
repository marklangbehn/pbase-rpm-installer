use mysql;

-- based on objects removed by mysql_secure_installation
delete from mysql.user where user='';
delete from mysql.user where user='root' and host not in ('localhost', '127.0.0.1', '::1');
drop database if exists test;
delete from mysql.db where Db='test' or Db='test\\_%';

-- init new application-user, and grant full permissions to app_db
create database app_db;

grant all privileges on app_db.* to 'dbappuser'@'localhost' identified by 'shomeddata' with grant option;

flush privileges;
