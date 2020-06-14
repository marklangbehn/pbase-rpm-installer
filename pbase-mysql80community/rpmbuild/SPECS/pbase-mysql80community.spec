Name: pbase-mysql80community
Version: 1.0
Release: 0
Summary: PBase MySQL 8.0 server rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-mysql80community-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-mysql80community
Requires: mysql-community-server,jq
## Requires: mysql-community-server,perl-DBD-mysql,jq

%description
Install MySQL 8.0 Community server

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

append_bashrc_alias() {
  if [ -z "$1" ]  ||  [ -z "$2" ]; then
    echo "Both params must be passed to postinstall.append_bashrc_alias()"
    exit 1
  fi

  EXISTING_ALIAS=$(grep $1 /root/.bashrc)
  if [[ "$EXISTING_ALIAS" == "" ]]; then
    echo "Adding shell alias:  $1"
    echo "alias $1='$2'"  >>  /root/.bashrc
  else
    echo "Already has shell alias '$1' in: /root/.bashrc"
  fi
}

check_linux_version() {
  AMAZON1_RELEASE=""
  AMAZON2_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2')"
    echo "system-release:          ${SYSTEM_RELEASE}"
  fi

  FEDORA_RELEASE=""
  if [[ -e "/etc/fedora-release" ]]; then
    FEDORA_RELEASE="$(cat /etc/fedora-release)"
    echo "fedora_release:          ${FEDORA_RELEASE}"
  fi

  REDHAT_RELEASE_DIGIT=""
  if [[ -e "/etc/redhat-release" ]]; then
    REDHAT_RELEASE_DIGIT="$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n1)"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "AMAZON1_RELEASE:         $AMAZON1_RELEASE"
    REDHAT_RELEASE_DIGIT="6"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON2_RELEASE" != "" ]]; then
    echo "AMAZON2_RELEASE:         $AMAZON2_RELEASE"
    REDHAT_RELEASE_DIGIT="7"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}


echo "PBase MySQL 8.0 Community server"

## config is stored in json file with root-only permsissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_mysql80community.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_mysql80community.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.json"
  PBASE_CONFIG_DIR="${PBASE_CONFIG_BASE}/module-config.d"

  PBASE_CONFIG_SEPARATE="${PBASE_CONFIG_DIR}/${PBASE_CONFIG_FILENAME}"
  PBASE_CONFIG_ALLINONE="${PBASE_CONFIG_BASE}/${PBASE_ALL_IN_ONE_CONFIG_FILENAME}"

  #echo "PBASE_CONFIG_SEPARATE:   $PBASE_CONFIG_SEPARATE"
  #echo "PBASE_CONFIG_ALLINONE:   $PBASE_CONFIG_ALLINONE"

  ## check if either file exists, assume SEPARATE as default
  PBASE_CONFIG="$PBASE_CONFIG_SEPARATE"

  if [[ -f "$PBASE_CONFIG_ALLINONE" ]] ; then
    PBASE_CONFIG="$PBASE_CONFIG_ALLINONE"
  fi

  if [[ -f "$PBASE_CONFIG" ]] ; then
    echo "Config file found:       $PBASE_CONFIG"
  else
    echo "Custom config not found: $PBASE_CONFIG"
  fi
}


parseConfig() {
  ## fallback when jq is not installed, use the default in the third param
  HAS_JQ_INSTALLED="$(which jq)"
  #echo "HAS_JQ_INSTALLED:   $HAS_JQ_INSTALLED"

  if [[ -z "$HAS_JQ_INSTALLED" ]] || [[ ! -f "$PBASE_CONFIG" ]] ; then
    ## echo "fallback to default: $3"
    eval "$1"="$3"
    return 1
  fi

  ## use jq to extract a json field named in the second param
  PARSED_VALUE="$(cat $PBASE_CONFIG  |  jq $2)"

  ## use eval to assign that to the variable named in the first param
  eval "$1"="$PARSED_VALUE"
}

## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

#echo "RAND_PW_USER:            $RAND_PW_USER"
#echo "RAND_PW_ROOT:            $RAND_PW_ROOT"

## look for either separate config file "pbase_mysql80community.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_mysql80community.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file

parseConfig "CONFIG_DB_HOSTNAME" ".pbase_mysql80community[0].default.hostName" "localhost"
parseConfig "CONFIG_DB_ROOTPSWD" ".pbase_mysql80community[0].default.rootPassword" $RAND_PW_ROOT
parseConfig "CONFIG_DB_PORT"     ".pbase_mysql80community[0].default.port" "3306"
parseConfig "CONFIG_DB_CHARSET"  ".pbase_mysql80community[0].default.characterSet" "utf8mb4"

parseConfig "CONFIG_DB_STARTSVC" ".pbase_mysql80community[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".pbase_mysql80community[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".pbase_mysql80community[0].default.database[0].name" "app_db"
parseConfig "CONFIG_DB_USER"     ".pbase_mysql80community[0].default.database[0].user" "dbappuser"
parseConfig "CONFIG_DB_PSWD"     ".pbase_mysql80community[0].default.database[0].password" $RAND_PW_USER

echo "CONFIG_DB_HOSTNAME:      $CONFIG_DB_HOSTNAME"
echo "CONFIG_DB_ROOTPSWD:      $CONFIG_DB_ROOTPSWD"
echo "CONFIG_DB_PORT:          $CONFIG_DB_PORT"
echo "CONFIG_DB_CHARSET:       $CONFIG_DB_CHARSET"

echo "CONFIG_DB_STARTSVC:      $CONFIG_DB_STARTSVC"
echo "CONFIG_DB_INSTALL:       $CONFIG_DB_INSTALL"
echo ""
echo "CONFIG_DB_NAME:          $CONFIG_DB_NAME"
echo "CONFIG_DB_USER:          $CONFIG_DB_USER"
echo "CONFIG_DB_PSWD:          $CONFIG_DB_PSWD"


## check which version of Linux is installed
check_linux_version

## Get hostname to be substituted in template config files
THISHOSTNAME="$(hostname)"
TMPLHOSTNAME="fiver.emosonic.com"

echo "MySQL configuration"
echo "Hostname:                $THISHOSTNAME"
#echo "Tmpl Host:               $TMPLHOSTNAME"

sed -i -e "s/$TMPLHOSTNAME/$THISHOSTNAME/g" /usr/local/pbase-data/pbase-mysql80community/mysql-init/create-user-dbappuser.sql

# Start and enable mysqld service at boot-time

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/service mysqld stop
else
  /bin/systemctl stop mysqld
fi


## replace my.cnf
## cp /usr/local/pbasedata/mysql-init/my.cnf /etc/my.cnf

## Port
#sed -i "s/3306/$CONFIG_DB_PORT/g" /etc/my.cnf


## create empty log file
touch /var/log/mysql-query.log
chown mysql:mysql /var/log/mysql-query.log



## option to configure MySQL's default character set
## currently only supporting setting to utf8mb4

if [ $CONFIG_DB_CHARSET == "utf8mb4" ]; then
  echo "Setting MySQL charset:   utf8mb4"

  if [ -d "/etc/my.cnf.d" ]; then
    echo "Config directory:        /etc/my.cnf.d/"

    ## copy the "utf8mb4" character set config to /etc
    echo "Config file:             /etc/my.cnf.d/character-set.cnf"
    /bin/cp --no-clobber /usr/local/pbase-data/pbase-mysql80community/mysql-init/character-set.cnf /etc/my.cnf.d/
  else
    echo "Config file:             /etc/my.cnf"
    echo "Not yet supported: utf8mb4"
  fi
fi


## initialization script
SRC_SCRIPT_DIR="/usr/local/pbase-data/pbase-mysql80community/mysql-init"
SCRIPT_DIR="/usr/local/pbase-data/pbase-mysql80community/mysql-init"
CREATE_USER_SCRIPT_MODS="create-user-dbappuser-mods.sql"

## make a copy of the create-user script
mkdir -p $SCRIPT_DIR
/bin/cp $SRC_SCRIPT_DIR/create-user-dbappuser.sql $SCRIPT_DIR/create-user-dbappuser-mods.sql

## default names and passwords in create-user script
TMPL_DB_NAME="app_db"
TMPL_DB_ROOTPSWD="SHOmeddata"
TMPL_APPUSER_NAME="dbappuser"
TMPL_APPUSER_PSWD="shomeddata"

## replace default names and passwords in with the ones from config-file
echo "Updating script:         $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS"

sed -i -e "s/$TMPL_DB_ROOTPSWD/$CONFIG_DB_ROOTPSWD/g" $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS
sed -i -e "s/$TMPL_DB_NAME/$CONFIG_DB_NAME/g" $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS
sed -i -e "s/$TMPL_APPUSER_NAME/$CONFIG_DB_USER/g" $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS
sed -i -e "s/$TMPL_APPUSER_PSWD/$CONFIG_DB_PSWD/g" $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS


## option to skip out of starting MySQL
if [ $CONFIG_DB_STARTSVC == "false" ]; then
    echo "startService is false, exiting"

	echo "Following steps:"
	echo "systemctl daemon-reload  ;  systemctl enable mysqld.service  ;   systemctl start mysqld"
	echo ""
    echo "Then, alter user:        root"
    echo "MYSQL_TMP_PWD:           $MYSQL_TMP_PWD"
    echo "MYSQL_ROOT_PWD:          $MYSQL_ROOT_PWD"

    ## mysql -uroot -p"$MYSQL_TMP_PWD"  --connect-expired-password mysql  -e"alter user 'root'@'localhost' identified by '$MYSQL_ROOT_PWD'"
    echo "SET_ROOT_CMD:            $SET_ROOT_CMD"

	echo "Then, run the script:    $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS"

	exit 0
fi

# Start and enable mysqld service at boot-time
if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig mysqld --level 345 on || fail "chkconfig failed to enable mysqld service"
  /sbin/service mysqld start || fail "failed to start mysqld service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl enable mysqld.service || fail "systemctl failed to enable mysqld service"
  /bin/systemctl start mysqld || fail "failed to start mysqld service"
fi


## transitional pswd
MYSQL_ROOT_PWD='ZSHOmed_data12-='
MYSQL_ROOT_PWD_AFTER=$CONFIG_DB_ROOTPSWD
MYSQL_DBAPPUSER_PWD=$CONFIG_DB_PSWD

MYSQL_TMP_PWD="$(echo "$a" | tac /var/log/mysqld.log | grep "A temporary password is generated for root@localhost: " | sed "s|^.*localhost: ||")"

echo "Temporary password:      $MYSQL_TMP_PWD"
echo "Transitional password:   $MYSQL_ROOT_PWD"
echo "MYSQL_ROOT_PWD_AFTER:    $MYSQL_ROOT_PWD_AFTER"


SET_ROOT_CMD='mysql -uroot -p"'
SET_ROOT_CMD+="$MYSQL_TMP_PWD"
SET_ROOT_CMD+='"  --connect-expired-password mysql  -e"'
SET_ROOT_CMD+="alter user 'root'@'localhost' identified by '"
SET_ROOT_CMD+="$MYSQL_ROOT_PWD"
SET_ROOT_CMD+="'"
SET_ROOT_CMD+='"'


## set root password
echo "Alter user:              root"
mysql -uroot -p"$MYSQL_TMP_PWD"  --connect-expired-password mysql  -e"alter user 'root'@'localhost' identified by '$MYSQL_ROOT_PWD'"


## run the modified script
echo "Running:                 mysql -uroot mysql  <  $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS"
mysql -uroot -p"$MYSQL_ROOT_PWD" --connect-expired-password mysql  <  $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS || fail "MySQL failed to create DB user dbappuser"


## add aliases
echo "" >> /root/.bashrc

if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
  append_bashrc_alias stopmysql "service mysql stop"
  append_bashrc_alias startmysql "service mysql start"
  append_bashrc_alias statusmysql "service mysql status"
  append_bashrc_alias restartmysql "service mysql restart"
else
  append_bashrc_alias stopmysql "/bin/systemctl stop mysql"
  append_bashrc_alias startmysql "/bin/systemctl start mysql"
  append_bashrc_alias statusmysql "/bin/systemctl status mysql"
  append_bashrc_alias restartmysql "/bin/systemctl restart mysql"
fi

append_bashrc_alias tailmysql "tail -f -n100 /var/log/mysqld.log"
append_bashrc_alias tailmysql0 "tail -f -n0 /var/log/mysqld.log"
append_bashrc_alias editmycnf "vi /etc/my.cnf"
append_bashrc_alias mysqlroot "mysql -u root -p mysql"
append_bashrc_alias mysqlappuser "mysql -u $CONFIG_DB_USER -p $CONFIG_DB_NAME"

echo " "
echo "MySQL root password:     $MYSQL_ROOT_PWD_AFTER"
echo "         DB created:     $CONFIG_DB_NAME"
echo "               user:     $CONFIG_DB_USER"
echo "           password:     $CONFIG_DB_PSWD"
echo " "
echo "connect with:            mysql -u root -p mysql"
echo "          or:            mysql -u $CONFIG_DB_USER -p $CONFIG_DB_NAME"
echo " "

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-mysql80community/mysql-init/my.cnf
/usr/local/pbase-data/pbase-mysql80community/mysql-init/character-set.cnf
/usr/local/pbase-data/pbase-mysql80community/mysql-init/create-user-dbappuser.sql
