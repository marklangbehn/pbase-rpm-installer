Name: pbase-postgres
Version: 1.0
Release: 3
Summary: PBase Postgres server rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-postgres-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-postgres
Requires: postgresql, postgresql-server, postgresql-contrib, postgresql-devel, jq, augeas

%description
Install PostgreSQL server

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
  AMAZON20XX_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2 ')"
    AMAZON20XX_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 20')"
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
  elif [[ "$AMAZON20XX_RELEASE" != "" ]]; then
    echo "AMAZON20XX_RELEASE:      $AMAZON20XX_RELEASE"
    REDHAT_RELEASE_DIGIT="9"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}

echo "PBase Postgres server"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## config is stored in json file with root-only permissions
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_postgres.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_postgres.json"
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

#echo "RAND_PW_USER:            $RAND_PW_USER"

## look for config file "pbase_postgres.json"
PBASE_CONFIG_FILENAME="pbase_postgres.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file

parseConfig "CONFIG_DB_HOSTNAME" ".pbase_postgres[0].default.hostName" "localhost"
parseConfig "CONFIG_DB_PORT"     ".pbase_postgres[0].default.port" "5432"

parseConfig "CONFIG_DB_STARTSVC" ".pbase_postgres[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".pbase_postgres[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".pbase_postgres[0].default.database[0].name" "app_db"
parseConfig "CONFIG_DB_USER"     ".pbase_postgres[0].default.database[0].user" "dbappuser"
parseConfig "CONFIG_DB_PSWD"     ".pbase_postgres[0].default.database[0].password" $RAND_PW_USER
parseConfig "CONFIG_DB_CHARSET"  ".pbase_postgres[0].default.database[0].characterSet" "UTF8"
parseConfig "CONFIG_CREATEDB"    ".pbase_postgres[0].default.database[0].grantCreateDatabase" "false"

echo "CONFIG_DB_HOSTNAME:      $CONFIG_DB_HOSTNAME"
echo "CONFIG_DB_PORT:          $CONFIG_DB_PORT"
echo "CONFIG_DB_CHARSET:       $CONFIG_DB_CHARSET"

echo "CONFIG_DB_STARTSVC:      $CONFIG_DB_STARTSVC"
echo "CONFIG_DB_INSTALL:       $CONFIG_DB_INSTALL"
echo ""
echo "CONFIG_DB_NAME:          $CONFIG_DB_NAME"
echo "CONFIG_DB_USER:          $CONFIG_DB_USER"
echo "CONFIG_DB_PSWD:          $CONFIG_DB_PSWD"

## fill PORT_NUM_SUFFIX only if using non-standard port number
PORT_NUM_SUFFIX=""

if [[ "${CONFIG_DB_PORT}" != "5432" ]]; then
  PORT_NUM_SUFFIX="${CONFIG_DB_PORT}"
fi

## Get hostname to be substituted in template config files
TARGETHOSTNAME="$(hostname)"

echo ""
echo "Postgres postinstall configuration"
echo "Hostname:                $TARGETHOSTNAME"

## check which version of Linux is installed
check_linux_version


if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  echo "Calling:                 service postgresql initdb"
  /sbin/service postgresql initdb
else
  echo "Calling:                 postgresql-setup --initdb --unit postgresql"
  /usr/bin/postgresql-setup --initdb --unit postgresql

  if [[ ! -d "/dir1/" ]] ; then
    echo "Creating:                /run/postgresql"
    mkdir -p /run/postgresql
    chown -R postgres:postgres /run/postgresql
  fi
fi

echo "Calling:                 systemctl daemon-reload"
/bin/systemctl daemon-reload

## configure pg_hba.conf
## make backup copy of file
/bin/cp "/var/lib/pgsql/data/pg_hba.conf" "/var/lib/pgsql/data/pg_hba.conf-PREV"


PG_HBA_CONF="/var/lib/pgsql/data/pg_hba.conf"

## use augeas to edit config file - change the connection method to md5
cat <<EOF | augtool --noload --noautoload
set /augeas/load/Pg_Hba
set /augeas/load/Pg_Hba/lens "Pg_Hba.lns"
set /augeas/load/Pg_Hba/incl[1] "/etc/postgresql/*/*/pg_hba.conf"
set /augeas/load/Pg_Hba/incl[2] "/var/lib/postgresql/*/data/pg_hba.conf"
set /augeas/load/Pg_Hba/incl[3] "/var/lib/pgsql/*/data/pg_hba.conf"
set /augeas/load/Pg_Hba/incl[4] "/var/lib/pgsql/data/pg_hba.conf"
load
set /files/var/lib/pgsql/data/pg_hba.conf/2/method md5
set /files/var/lib/pgsql/data/pg_hba.conf/3/method md5
save
EOF


## allow remote access
TRUST_ALL_LINE="host    all             all             0.0.0.0/0               md5"
#TRUST_ALL_LINE="host    all             all             0.0.0.0/0               trust"

echo "Adding login config to:  /var/lib/pgsql/data/pg_hba.conf"
echo "                         ${TRUST_ALL_LINE}"

echo ""                   >> ${PG_HBA_CONF}
echo "${TRUST_ALL_LINE}"  >> ${PG_HBA_CONF}


## configure postgresql.conf

LISTENADDR_ALL_LINE="listen_addresses = '*'"
SEARCH_LISTENADDR_SET="^${LISTENADDR_ALL_LINE}"
SEARCH_LISTENADDR_DFLT="#listen_addresses"
REPLACE_LISTENER_LINE="${LISTENADDR_ALL_LINE}\n${SEARCH_LISTENADDR_DFLT}"

MAX_CONNECTIONS_LINE_DFT="max_connections = 100"
SEARCH_MAX_CONNECTIONS_LINE="^max_connections = 100"
REPLACE_MAX_CONNECTIONS_LINE="max_connections = 500"

POSTGRES_CONF_FILE="/var/lib/pgsql/data/postgresql.conf"

if [[ -e ${POSTGRES_CONF_FILE} ]]; then
  echo "Configuring:             ${POSTGRES_CONF_FILE}"

  ALREADY_HAS_LISTENADDR=`grep "${SEARCH_LISTENADDR_SET}" "${POSTGRES_CONF_FILE}"`
  ##echo "ALREADY_HAS_LISTENADDR:      ${ALREADY_HAS_LISTENADDR}"

  if [[ "${ALREADY_HAS_LISTENADDR}" == "" ]]; then
    ## make backup copy of file
    /bin/cp "${POSTGRES_CONF_FILE}" "${POSTGRES_CONF_FILE}-PREV"

    echo "Setting:                 ${LISTENADDR_ALL_LINE}"
    sed -i "s/${SEARCH_LISTENADDR_DFLT}/${REPLACE_LISTENER_LINE}/" "${POSTGRES_CONF_FILE}"
  else
    echo "Already has modified listen_addresses value. Leaving unchanged."
  fi

  HAS_DFLT_MAX_CONNECTIONS=`grep "${MAX_CONNECTIONS_LINE_DFT}" "${POSTGRES_CONF_FILE}"`
  ##echo "HAS_DFLT_MAX_CONNECTIONS:  ${HAS_DFLT_MAX_CONNECTIONS}"

  if [[ "${HAS_DFLT_MAX_CONNECTIONS}" != "" ]]; then
    echo "Setting:                 ${REPLACE_MAX_CONNECTIONS_LINE}"
    sed -i "s/${SEARCH_MAX_CONNECTIONS_LINE}/${REPLACE_MAX_CONNECTIONS_LINE}/" "${POSTGRES_CONF_FILE}"
  else
    echo "Already has modified max_connections value. Leaving unchanged."
  fi

fi


## check if using non-standard port

if [[ "${PORT_NUM_SUFFIX}" != "" ]]; then
  if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
    ## on EL6 modify postgres.conf
    ALREADY_HAS_PORT_EQ_SET=$(grep "${CONFIG_DB_PORT}" "/etc/init.d/postgresql")
    #echo "ALREADY_HAS_PORT_EQ_SET:      ${ALREADY_HAS_PORT_EQ_SET}"

    if [[ "${ALREADY_HAS_PORT_EQ_SET}" == "" ]]; then
      echo "Customize service:       /etc/init.d/postgresql"

      sed -i "s/5432/${CONFIG_DB_PORT}/" "/etc/init.d/postgresql"
      PORT_NUM_SUFFIX=" --port=${CONFIG_DB_PORT}"
    else
      echo "Already has modified port value. Leaving unchanged."
    fi
  else
    ## on EL7+ add systemd include file
    echo "Custom systemd config:   /etc/systemd/system/postgresql.service"
    /bin/cp --no-clobber /usr/local/pbase-data/pbase-postgres/etc-systemd-system/postgresql.service  /etc/systemd/system/
    sed -i "s/5432/${CONFIG_DB_PORT}/" "/etc/systemd/system/postgresql.service"

    ## modify port number in postgresql.conf
    #PORT_EQ_LINE_START="port = "
    #PORT_EQ_LINE_ALREADY_SET="^${PORT_EQ_LINE_START}"
    #ALREADY_HAS_PORT_EQ_SET=$(grep "${PORT_EQ_LINE_ALREADY_SET}" "${POSTGRES_CONF_FILE}")
    #echo "ALREADY_HAS_PORT_EQ_SET:      ${ALREADY_HAS_PORT_EQ_SET}"

    #if [[ "${ALREADY_HAS_PORT_EQ_SET}" == "" ]]; then
    #  echo "Setting:                 ${PORT_EQ_LINE_START}${CONFIG_DB_PORT}"
    #  sed -i "s/^#port = [[:digit:]]\+/port = ${CONFIG_DB_PORT}/" "${POSTGRES_CONF_FILE}"
    #else
    #  echo "Already has modified port value. Leaving unchanged."
    #fi

    PORT_NUM_SUFFIX=" --port=${CONFIG_DB_PORT}"
  fi
fi


# Start and enable postgresql service at boot-time
echo "Starting Service:        postgresql"


if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig postgresql --level 345 on || fail "chkconfig failed to enable postgresql service"
  /sbin/service postgresql start || fail "failed to start postgresql service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl enable --now postgresql.service || fail "systemctl failed to enable postgresql service"
  /bin/systemctl start postgresql || fail "failed to restart postgresql service"
fi


## make a copy of the create-user script
SRC_SCRIPT_DIR="/usr/local/pbase-data/pbase-postgres/postgres-init"
SCRIPT_DIR="/usr/local/pbase-data/admin-only/postgres-init"

echo "Script:                  $SCRIPT_DIR"
echo "Create user script:      $SCRIPT_DIR/create-dbappuser-mods.sql"

mkdir -p $SCRIPT_DIR
/bin/cp $SRC_SCRIPT_DIR/create-dbappuser.sql $SCRIPT_DIR/create-dbappuser-mods.sql
TMPL_APPUSER_NAME="dbappuser"
TMPL_APPUSER_PSWD="shomeddata"

## edit the script with values found in module-config.json
sed -i -e "s/$TMPL_APPUSER_NAME/$CONFIG_DB_USER/g" $SCRIPT_DIR/create-dbappuser-mods.sql
sed -i -e "s/$TMPL_APPUSER_PSWD/$CONFIG_DB_PSWD/g" $SCRIPT_DIR/create-dbappuser-mods.sql

if [[ $CONFIG_CREATEDB == "true" ]]; then
  echo "Granting createdb:       $CONFIG_DB_USER"
  echo "alter user $CONFIG_DB_USER with createdb" >> $SCRIPT_DIR/create-dbappuser-mods.sql
fi

## create the user, then the database owned by that user
echo "Creating Postgres user:  $CONFIG_DB_USER"

su - postgres -c "psql${PORT_NUM_SUFFIX} -a -f $SCRIPT_DIR/create-dbappuser-mods.sql"

echo "Creating database:       createdb${PORT_NUM_SUFFIX} -E ${CONFIG_DB_CHARSET} -T template0 -O ${CONFIG_DB_USER} ${CONFIG_DB_NAME}"
su - postgres -c "createdb${PORT_NUM_SUFFIX} -E ${CONFIG_DB_CHARSET} -T template0 -O ${CONFIG_DB_USER} ${CONFIG_DB_NAME}"

echo "Next step - optional - login with:"
echo ""
echo "su - postgres"
echo "psql${PORT_NUM_SUFFIX}"
echo ""
#echo "  or if remote access is enabled:"
#echo "psql --host=$TARGETHOSTNAME --username=$CONFIG_DB_USER --dbname=$CONFIG_DB_NAME --password"
#echo ""


## Add aliases helpful for admin tasks to .bashrc

append_bashrc_alias editpostgreshba "vi /var/lib/pgsql/data/pg_hba.conf"
append_bashrc_alias editpostgresconf "vi /var/lib/pgsql/data/postgresql.conf"

if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
  append_bashrc_alias stoppostgres "service postgres stop"
  append_bashrc_alias startpostgres "service postgres start"
  append_bashrc_alias statuspostgres "service postgres status"
  append_bashrc_alias restartpostgres "service postgres restart"
else
  append_bashrc_alias stoppostgres "/bin/systemctl stop postgresql"
  append_bashrc_alias startpostgres "/bin/systemctl start postgresql"
  append_bashrc_alias statuspostgres "/bin/systemctl status postgresql"
  append_bashrc_alias restartpostgres "/bin/systemctl restart postgresql"
fi


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-postgres/postgres-init/create-dbappuser.sql
/usr/local/pbase-data/pbase-postgres/etc-systemd-system/postgresql.service
