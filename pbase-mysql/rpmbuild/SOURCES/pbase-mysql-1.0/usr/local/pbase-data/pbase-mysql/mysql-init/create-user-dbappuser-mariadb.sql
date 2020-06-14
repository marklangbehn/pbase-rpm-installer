use mysql;

-- based on things removed by mysql_secure_installation
delete from mysql.user where user='';
delete from mysql.user where user='root' and host not in ('localhost', '127.0.0.1', '::1');
drop database if exists test;
delete from mysql.db where Db='test' or Db='test\\_%';


-- set root pswd for MariaDB
set password for 'root'@'localhost' = password('SHOmeddata');
flush privileges;

-- init new application-user, grant full permissions to app_db
create database app_db;

create user 'dbappuser'@'localhost' identified by 'shomeddata';
grant all privileges on app_db.* to 'dbappuser'@'localhost' with grant option;

create user 'dbappuser'@'%' identified by 'shomeddata';
grant all privileges on app_db.* to 'dbappuser'@'%' with grant option;

-- alter user 'dbappuser'@'localhost' identified by 'shomeddata';
-- alter user 'dbappuser'@'%' identified by 'shomeddata';

-- new replication user
-- create user 'repluser'@'%' identified by 'SHOmeddata12-=';
-- grant replication slave on *.* to 'repluser'@'%';

flush privileges;
