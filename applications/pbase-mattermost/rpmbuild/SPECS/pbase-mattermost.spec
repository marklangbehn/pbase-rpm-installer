Name: pbase-mattermost
Version: 1.0
Release: 0
Summary: PBase Mattermost service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-mattermost-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-mattermost
Requires: pbase-apache, wget, tar, jq

%description
PBase Mattermost service

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
# echo "rpm postinstall $1"

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

copy_if_not_exists() {
  if [ -z "$1" ]  ||  [ -z "$2" ]  ||  [ -z "$3" ]; then
    echo "All 3 params must be passed to copy_if_not_exists function"
    exit 1
  fi

  FILENAME="$1"
  SOURCE_DIR="$2"
  DEST_DIR="$3"

  SOURCE_FILE_PATH=$SOURCE_DIR/$FILENAME
  DEST_FILE_PATH=$DEST_DIR/$FILENAME

  if [[ -f "$DEST_FILE_PATH" ]] ; then
    echo "Already exists:          $DEST_FILE_PATH"
    return 0
  else
    echo "Copying file:            $DEST_FILE_PATH"
    /bin/cp -rf --no-clobber $SOURCE_FILE_PATH  $DEST_DIR
    return 1
  fi
}


echo "PBase Mattermost service"

## config is stored in json file with root-only permissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_mattermost.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_mattermost.json"
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


## Mattermost config
## look for either separate config file "pbase_mattermost.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_mattermost.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "HTTP_PORT" ".pbase_mattermost.httpPort" "8065"
parseConfig "ADD_APACHE_PROXY" ".pbase_mattermost.addApacheProxy" "false"
parseConfig "USE_SUB_DOMAIN" ".pbase_mattermost.useSubDomain" "false"
parseConfig "SUB_DOMAIN_NAME" ".pbase_mattermost.subDomainName" "mattermost"

echo "HTTP_PORT:               $HTTP_PORT"
echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"
echo "USE_SUB_DOMAIN:          $USE_SUB_DOMAIN"
echo "SUB_DOMAIN_NAME:         $SUB_DOMAIN_NAME"


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"
echo "RAND_PW_ROOT:            $RAND_PW_ROOT"


## Database config
PBASE_CONFIG_FILENAME="pbase_mysql80community.json"
PBASE_CONFIG_NAME="pbase_mysql80community"

if [[ -e "/usr/local/pbase-data/admin-only/module-config.d/pbase_mysql80community.json" ]] ; then
  PBASE_CONFIG_FILENAME="pbase_mysql80community.json"
  PBASE_CONFIG_NAME="pbase_mysql80community"
elif [[ -e "/usr/local/pbase-data/admin-only/module-config.d/pbase_mysql.json" ]] ; then
  PBASE_CONFIG_FILENAME="pbase_mysql.json"
  PBASE_CONFIG_NAME="pbase_mysql"
elif [[ -e "/usr/local/pbase-data/admin-only/module-config.d/pbase_postgres.json" ]] ; then
  PBASE_CONFIG_FILENAME="pbase_postgres.json"
  PBASE_CONFIG_NAME="pbase_postgres"
else
  PBASE_CONFIG_FILENAME="pbase_mysql.json"
  PBASE_CONFIG_NAME="pbase_mysql"
fi

echo "PBASE_CONFIG_FILENAME:   $PBASE_CONFIG_FILENAME"
echo "PBASE_CONFIG_NAME:       $PBASE_CONFIG_NAME"


locateConfigFile "${PBASE_CONFIG_FILENAME}"

## fetch config value from JSON file

parseConfig "CONFIG_DB_HOSTNAME" ".${PBASE_CONFIG_NAME}[0].default.hostName" "localhost"
parseConfig "CONFIG_DB_PORT"     ".${PBASE_CONFIG_NAME}[0].default.port" "3306"
parseConfig "CONFIG_DB_CHARSET"  ".${PBASE_CONFIG_NAME}[0].default.characterSet" "utf8mb4"

parseConfig "CONFIG_DB_STARTSVC" ".${PBASE_CONFIG_NAME}[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".${PBASE_CONFIG_NAME}[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".${PBASE_CONFIG_NAME}[0].default.database[0].name" "mattermost"
parseConfig "CONFIG_DB_USER"     ".${PBASE_CONFIG_NAME}[0].default.database[0].user" "mmuser"
parseConfig "CONFIG_DB_PSWD"     ".${PBASE_CONFIG_NAME}[0].default.database[0].password" $RAND_PW_USER

echo "CONFIG_DB_HOSTNAME:      $CONFIG_DB_HOSTNAME"
echo "CONFIG_DB_PORT:          $CONFIG_DB_PORT"
echo "CONFIG_DB_CHARSET:       $CONFIG_DB_CHARSET"

echo "CONFIG_DB_STARTSVC:      $CONFIG_DB_STARTSVC"
echo "CONFIG_DB_INSTALL:       $CONFIG_DB_INSTALL"
echo ""
echo "CONFIG_DB_NAME:          $CONFIG_DB_NAME"
echo "CONFIG_DB_USER:          $CONFIG_DB_USER"
echo "CONFIG_DB_PSWD:          $CONFIG_DB_PSWD"



## check if already installed
if [[ -d "/opt/mattermost" ]]; then
  echo "/opt/mattermost directory already exists - exiting"
  exit 0
fi

echo "Downloading Mattermost server binary from releases.mattermost.com"

## https://releases.mattermost.com/5.27.0/mattermost-5.27.0-linux-amd64.tar.gz
##TODO how to find latest version dynamically?
VER="5.27.0"

cd /usr/local/pbase-data/pbase-mattermost
wget -q -O mattermost.tar.gz https://releases.mattermost.com/${VER}/mattermost-${VER}-linux-amd64.tar.gz

echo "Downloaded file:"
ls -lh mattermost.tar.gz
chown root:root mattermost.tar.gz

echo "Installed in directory:  /opt/mattermost"
tar zxf mattermost.tar.gz -C /opt

mkdir /opt/mattermost/data

echo "Creating group and user: mattermost"
useradd -U -M -d /opt/mattermost mattermost

chown -R mattermost:mattermost /opt/mattermost
chmod -R g+w /opt/mattermost

/bin/cp --no-clobber /opt/mattermost/config/config.json /opt/mattermost/config/config.json-ORIG

## sample after editing the config file's datasource line
##     "DataSource": "mmuser:shomeddata@tcp(localhost:3306)/mattermost?charset=utf8mb4,utf8\u0026readTimeout=30s\u0026writeTimeout=30s",

echo "Updating config:         /opt/mattermost/config/config.json"
echo "Enabling service:        /etc/systemd/system/mattermost"

/bin/cp --no-clobber /usr/local/pbase-data/pbase-mattermost/etc-systemd-system/mattermost.service /etc/systemd/system/
chmod 664 /etc/systemd/system/mattermost.service


if [[ $PBASE_CONFIG_NAME == "pbase_postgres" ]] ; then
  echo "Setting Postgres connection"
  sed -i -e "s/mysqld.service/postgresql.service/" /etc/systemd/system/mattermost.service

  sed -i -e "s/mysql/postgres/" /opt/mattermost/config/config.json
  sed -i -e "s/mmuser\:mostest/postgres:\/\/mmuser:mostest/" /opt/mattermost/config/config.json
  sed -i -e "s/charset\=utf8mb4\,utf8/sslmode=disable\&connect_timeout=10/" /opt/mattermost/config/config.json
  sed -i -e "s/tcp(localhost\:3306)/localhost:5432/" /opt/mattermost/config/config.json
  sed -i -e "s/\\\u0026readTimeout=30s//" /opt/mattermost/config/config.json
  sed -i -e "s/\\\u0026writeTimeout=30s//" /opt/mattermost/config/config.json

  sed -i -e "s/mmuser/$CONFIG_DB_USER/" /opt/mattermost/config/config.json
  sed -i -e "s/mostest/$CONFIG_DB_PSWD/" /opt/mattermost/config/config.json
  sed -i -e "s/mattermost_test/$CONFIG_DB_NAME/" /opt/mattermost/config/config.json
  sed -i -e "s/utf8mb4/utf8/" /opt/mattermost/config/config.json
else
  echo "Setting MySQL connection"
  sed -i -e "s/mmuser/$CONFIG_DB_USER/" /opt/mattermost/config/config.json
  sed -i -e "s/mostest/$CONFIG_DB_PSWD/" /opt/mattermost/config/config.json
  sed -i -e "s/mattermost_test/$CONFIG_DB_NAME/" /opt/mattermost/config/config.json
  ## sed -i -e "s/utf8mb4/utf8/" /opt/mattermost/config/config.json
fi


systemctl daemon-reload
systemctl enable mattermost

echo "Starting service:        /etc/systemd/system/mattermost"

systemctl start mattermost
systemctl status mattermost


## add shell aliases
append_bashrc_alias tailmattermost "tail -f /opt/mattermost/logs/mattermost.log"
append_bashrc_alias editmattermostconf "vi /opt/mattermost/config/config.json"

echo "Mattermost service running. Open this URL to complete install."

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"


if [[ "$USE_SUB_DOMAIN" == "true" ]] && [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  PROXY_CONF="/etc/httpd/conf.d/mattermost-proxy-subdomain.conf"
  echo "Adding ${SUB_DOMAIN_NAME} subdomain proxy to mattermost application"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy-subdomain.conf /etc/httpd/conf.d/

  echo "Updating config file:    ${PROXY_CONF}"

  sed -i "s/mysubdomain.mydomain.com/${SUB_DOMAIN_NAME}.${THISDOMAINNAME}/" $PROXY_CONF

  systemctl daemon-reload
  systemctl restart httpd

  echo "                         http://${SUB_DOMAIN_NAME}.${THISDOMAINNAME}/install"
  echo "or"
  echo "                         http://localhost/install"

elif [[ "$ADD_APACHE_PROXY" == "true" ]] ; then

  echo "Adding / proxy to mattermost"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy.conf /etc/httpd/conf.d/

  PROXY_CONF="/etc/httpd/conf.d/mattermost-proxy.conf"
  echo "Updating config file:    ${PROXY_CONF}"

  sed -i "s/mydomain.com/${THISDOMAINNAME}/" $PROXY_CONF

  systemctl daemon-reload
  systemctl restart httpd

  echo "                         http://${THISDOMAINNAME}/install"
  echo "or"
  echo "                         http://localhost/install"

else

  echo "                         http://${THISDOMAINNAME}:8065/install"
  echo "or"
  echo "                         http://localhost:8065/install"
fi

echo ""


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-mattermost/etc-systemd-system/mattermost.service
/usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy.conf
/usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy-subdomain.conf
