use mysql;

-- reduce password-validation limits
set global validate_password.length = 8;
set global validate_password.number_count = 0;
set global validate_password.mixed_case_count = 0;
set global validate_password.special_char_count = 0;

## alter user 'root'@'localhost' identified by 'SHOmeddata';
alter user 'root'@'localhost' identified with mysql_native_password by 'SHOmeddata';

-- new dbappuser user grant full permissions to app_db
create database app_db;

create user 'dbappuser'@'localhost' identified by 'shomeddata';
grant all privileges on app_db.* to 'dbappuser'@'localhost' with grant option;

create user 'dbappuser'@'%' identified by 'shomeddata';
grant all privileges on app_db.* to 'dbappuser'@'%' with grant option;

-- use the native password
alter user 'dbappuser'@'localhost' identified with mysql_native_password by 'shomeddata';
alter user 'dbappuser'@'%' identified with mysql_native_password by 'shomeddata';

-- new replication user
-- create user 'repluser'@'%' identified by 'SHOmeddata12-=';
-- grant replication slave on *.* to 'repluser'@'%';

flush privileges;
