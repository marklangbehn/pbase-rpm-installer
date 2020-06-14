Name: pbase-mysql
Version: 1.0
Release: 0
Summary: PBase MySQL server rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-mysql-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-mysql
Requires: pbase-mysql-transitive-dep,perl-DBD-mysql,jq

%description
Install MySQL server

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


echo "PBase MySQL server"

## config is stored in json file with root-only permsissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_mysql.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_mysql.json"
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

## look for either separate config file "pbase_mysql.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_mysql.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file

parseConfig "CONFIG_DB_HOSTNAME" ".pbase_mysql[0].default.hostName" "localhost"
parseConfig "CONFIG_DB_ROOTPSWD" ".pbase_mysql[0].default.rootPassword" $RAND_PW_ROOT
parseConfig "CONFIG_DB_PORT"     ".pbase_mysql[0].default.port" "3306"
parseConfig "CONFIG_DB_CHARSET"  ".pbase_mysql[0].default.characterSet" "utf8mb4"

parseConfig "CONFIG_DB_STARTSVC" ".pbase_mysql[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".pbase_mysql[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".pbase_mysql[0].default.database[0].name" "app_db"
parseConfig "CONFIG_DB_USER"     ".pbase_mysql[0].default.database[0].user" "dbappuser"
parseConfig "CONFIG_DB_PSWD"     ".pbase_mysql[0].default.database[0].password" $RAND_PW_USER

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


# Start and enable mysqld service at boot-time

#if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
#  /sbin/service mysqld stop
#else
#  /bin/systemctl stop mysqld
#fi


## replace my.cnf
## cp /usr/local/pbasedata/mysql-init/my.cnf /etc/my.cnf

## Port
#sed -i "s/3306/$CONFIG_DB_PORT/g" /etc/my.cnf


## check which version of MySQL is installed
## the UTF8MB4 configuration cannot be done versions 5.0 and 5.1
MYSQL_IS_50="$(mysql --version  | grep '5\.0\.')"
MYSQL_IS_51="$(mysql --version  | grep '5\.1\.')"
IS_MYSQL51="false"

if [[ "$MYSQL_IS_50" != "" ]] || [[ "$MYSQL_IS_51" != "" ]]; then
  IS_MYSQL51="true"
fi

#echo "IS_MYSQL51:              $IS_MYSQL51"


## create empty log file
touch /var/log/mysql-query.log
#chown mysql:mysql /var/log/mysql-query.log


# Start and enable mysqld service at boot-time

CREATE_USER_SCRIPT="create-user-dbappuser.sql"
CREATE_USER_SCRIPT_MODS="create-user-dbappuser-mods.sql"

CREATE_USER_SCRIPT_MARIADB="create-user-dbappuser-mariadb.sql"
CREATE_USER_SCRIPT_MARIADB_MODS="create-user-dbappuser-mariadb-mods.sql"

CREATE_USER_SCRIPT_MYSQL5="create-user-dbappuser-mysql5.sql"
CREATE_USER_SCRIPT_MYSQL5_MODS="create-user-dbappuser-mysql5-mods.sql"

## check which installed: mariadb  or mysql
MARIADB_SERVICE="/usr/lib/systemd/system/mariadb.service"
MYSQL_SVC_NAME="mysqld"

if [[ -f "${MARIADB_SERVICE}" ]]; then
  CREATE_USER_SCRIPT="$CREATE_USER_SCRIPT_MARIADB"
  CREATE_USER_SCRIPT_MODS="$CREATE_USER_SCRIPT_MARIADB_MODS"
  MYSQL_SVC_NAME="mariadb"
fi

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  CREATE_USER_SCRIPT="$CREATE_USER_SCRIPT_MYSQL5"
  CREATE_USER_SCRIPT_MODS="$CREATE_USER_SCRIPT_MYSQL5_MODS"
fi

echo "MYSQL_SVC_NAME:          $MYSQL_SVC_NAME"


MYSQL_ROOT_PWD='$HOmeddata12-='
MYSQL_ROOT_PWD_AFTER=$CONFIG_DB_ROOTPSWD
MYSQL_DBAPPUSER_PWD=$CONFIG_DB_PSWD

## echo "CREATE_USER_SCRIPT_MODS: $CREATE_USER_SCRIPT_MODS"

## initialization script
SRC_SCRIPT_DIR="/usr/local/pbase-data/pbase-mysql/mysql-init"
SCRIPT_DIR="/usr/local/pbase-data/admin-only/mysql-init"

## make a copy of the create-user script
mkdir -p $SCRIPT_DIR
/bin/cp $SRC_SCRIPT_DIR/$CREATE_USER_SCRIPT $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS

echo "Create user script:      $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS"

## edit-in-place the create-user script
sed -i -e "s/$TMPLHOSTNAME/$THISHOSTNAME/g" $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS

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

## option to configure MySQL's default character set
## currently only supporting setting to utf8mb4

if [[ "$CONFIG_DB_CHARSET" == "utf8mb4" ]] && [ -d "/etc/my.cnf.d" ]; then
  echo "Setting MySQL charset:   utf8mb4"
  echo "Config directory:        /etc/my.cnf.d/"

  ## copy the "utf8mb4" character set config to /etc
  echo "Config file:             /etc/my.cnf.d/character-set.cnf"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-mysql/mysql-init/character-set.cnf /etc/my.cnf.d/

elif [[ "$CONFIG_DB_CHARSET" == "utf8mb4" ]] && [[ "$IS_MYSQL51" == "true" ]]; then
  echo "Not supported:           utf8mb4"
  echo "Leaving unchanged:       /etc/my.cnf"

elif [[ "$CONFIG_DB_CHARSET" == "utf8mb4" ]] && [[ -e "/etc/my.cnf" ]]; then
  echo "Config file:             /etc/my.cnf"

file="/etc/my.cnf"
file_copy="/etc/my-copy.cnf"
file_out1="/etc/my-edited1.cnf"

/bin/cp --no-clobber $file $file_copy

HAS_CLIENT=$(grep "\[client\]" $file)
HAS_MYSQL=$(grep "\[mysql\]" $file)
HAS_MYSQLD=$(grep "\[mysqld\]" $file)

echo "HAS_CLIENT:  $HAS_CLIENT"
echo "HAS_MYSQL:   $HAS_MYSQL"
echo "HAS_MYSQLD:  $HAS_MYSQLD"

if [[ "$HAS_CLIENT" != "" ]]; then
  echo "editing [client] section"
  awk '/\[client\]/ {$0=$0"\n# set UTF8 client encoding\ndefault-character-set = utf8mb4\n"}1' q="'" $file > $file_out1
  /bin/cp -f $file_out1 $file
else
  echo "adding [client] section"
  echo '' >> $file
  echo '[client]' >> $file
  echo '# set UTF8 client encoding' >> $file
  echo 'default-character-set = utf8mb4' >> $file
fi

if [[ "$HAS_MYSQL" != "" ]]; then
  echo "editing [mysql] section"
  awk '/\[mysql\]/ {$0=$0"\n# set UTF8 encoding\ndefault-character-set = utf8mb4\n"}1' q="'" $file > $file_out1
  /bin/cp -f $file_out1 $file
else
  echo "adding [mysql] section"
  echo '' >> $file
  echo '[mysql]' >> $file
  echo '# set UTF8 encoding' >> $file
  echo 'default-character-set = utf8mb4' >> $file
fi

if [[ "$HAS_MYSQLD" != "" ]]; then
  echo "editing [mysqld] section"
  awk '/\[mysqld\]/ {$0=$0"\n# set UTF8 default collation\ncollation-server = utf8_unicode_ci\ninit-connect="q"SET NAMES utf8"q"\ncharacter-set-server = utf8\ncharacter-set-client-handshake = FALSE\n"}1' q="'" $file > $file_out1
  /bin/cp -f $file_out1 $file
else
  echo "adding [mysqld] section"
  echo '' >> $file
  echo '[mysqld]' >> $file
  echo '# set UTF8 default collation' >> $file
  echo 'collation-server = utf8_unicode_ci' >> $file
  echo 'init-connect="SET NAMES utf8"' >> $file
  echo 'character-set-client-handshake = FALSE' >> $file
fi

echo "done:   $file"

fi

## option to skip out of starting MySQL
if [ $CONFIG_DB_STARTSVC == "false" ]; then
	echo "startService is false, exiting"
	exit 0
fi

# Start and enable mysqld/mariadb service at boot-time
if [[ -f "${MARIADB_SERVICE}" ]]; then
  echo "Starting mariadb.service"
  /bin/systemctl daemon-reload
  /bin/systemctl enable mariadb.service || fail "systemctl failed to enable mariadb service"
  /bin/systemctl start mariadb || fail "failed to start mariadb service"
elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  echo "Starting mysqld"
  /sbin/chkconfig mysqld --level 345 on || fail "chkconfig failed to enable mysqld service"
  /sbin/service mysqld start || fail "failed to start mysqld service"
else
  echo "Starting mysqld.service"
  /bin/systemctl daemon-reload
  /bin/systemctl enable mysqld.service || fail "systemctl failed to enable mysqld service"
  /bin/systemctl start mysqld || fail "failed to start mysqld service"
fi


## run the modified script
echo "Running:                 mysql -uroot mysql  <  $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS"
mysql -uroot mysql  <  $SCRIPT_DIR/$CREATE_USER_SCRIPT_MODS || fail "MySQL failed to create DB user dbappuser"


## set the root pswd for MySQL 5 -- ##REVISIT how to do for MySQL 5.x only? here it assumes if running on RHEL6, then it's MYSQL5
if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  echo "Set DB root password"
  echo "Executing:               mysqladmin -u root password $CONFIG_DB_ROOTPSWD"
  mysqladmin -u root password "$CONFIG_DB_ROOTPSWD"
fi


## add aliases
echo "" >> /root/.bashrc

if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
  append_bashrc_alias stopmysql "service mysqld stop"
  append_bashrc_alias startmysql "service mysqld start"
  append_bashrc_alias statusmysql "service mysqld status"
  append_bashrc_alias restartmysql "service mysqld restart"
else
  append_bashrc_alias stopmysql "/bin/systemctl stop mysqld"
  append_bashrc_alias startmysql "/bin/systemctl start mysqld"
  append_bashrc_alias statusmysql "/bin/systemctl status mysqld"
  append_bashrc_alias restartmysql "/bin/systemctl restart mysqld"
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
/usr/local/pbase-data/pbase-mysql/mysql-init/my.cnf
/usr/local/pbase-data/pbase-mysql/mysql-init/character-set.cnf
/usr/local/pbase-data/pbase-mysql/mysql-init/create-user-dbappuser.sql
/usr/local/pbase-data/pbase-mysql/mysql-init/create-user-dbappuser-mysql5.sql
/usr/local/pbase-data/pbase-mysql/mysql-init/create-user-dbappuser-mariadb.sql
