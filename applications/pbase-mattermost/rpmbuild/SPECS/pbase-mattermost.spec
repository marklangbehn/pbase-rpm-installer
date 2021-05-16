Name: pbase-mattermost
Version: 1.0
Release: 1
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

## config is stored in json file with root-only permissions
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/


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

echo "PBase Mattermost service"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## check if already installed
if [[ -d "/opt/mattermost" ]]; then
  echo "/opt/mattermost directory already exists - exiting"
  exit 0
fi

## Mattermost config
## look for config file "pbase_mattermost.json"
PBASE_CONFIG_FILENAME="pbase_mattermost.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "HTTP_PORT" ".pbase_mattermost.port" "8065"
parseConfig "ADD_APACHE_PROXY" ".pbase_mattermost.addApacheProxy" "false"

echo "HTTP_PORT:               $HTTP_PORT"
echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"


## Apache config
PBASE_CONFIG_FILENAME="pbase_apache.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

if [[ -e "/usr/local/pbase-data/admin-only/module-config.d/pbase_apache.json" ]] ; then
  parseConfig "APACHE_SERVER_ADMIN" ".pbase_apache.serverAdmin" ""
  echo "APACHE_SERVER_ADMIN:     ${APACHE_SERVER_ADMIN}"
else
  echo "No apache config:        pbase_apache.json"
fi


## Let's Encrypt config
PBASE_CONFIG_FILENAME="pbase_lets_encrypt.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"
URL_SUBDOMAIN=""
QT="'"
URL_SUBDOMAIN_QUOTED="${QT}${QT}"

if [[ -e "/usr/local/pbase-data/admin-only/module-config.d/pbase_lets_encrypt.json" ]] ; then
  parseConfig "URL_SUBDOMAIN" ".pbase_lets_encrypt.urlSubDomain" ""
  URL_SUBDOMAIN_QUOTED=${QT}${URL_SUBDOMAIN}${QT}
  echo "URL_SUBDOMAIN:           ${URL_SUBDOMAIN_QUOTED}"
else
  echo "No subdomain config:     pbase_lets_encrypt.json"
fi


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

if [[ "${PBASE_CONFIG_NAME}" == "pbase_postgres" ]] ; then
  parseConfig "CONFIG_DB_CHARSET"  ".${PBASE_CONFIG_NAME}[0].default.database[0].characterSet" "UTF8"
else
  parseConfig "CONFIG_DB_CHARSET"  ".${PBASE_CONFIG_NAME}[0].default.characterSet" "utf8mb4"
fi

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
echo ""

PBASE_CONFIG_FILENAME="pbase_lets_encrypt.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "CONFIG_ENABLE_AUTORENEW" ".pbase_lets_encrypt.enableAutoRenew" "true"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_lets_encrypt.executeCertbotCmd" "true"

parseConfig "EMAIL_ADDR" ".pbase_lets_encrypt.emailAddress" "yoursysadmin@yourrealmail.com"
parseConfig "ADDITIONAL_SUBDOMAIN" ".pbase_lets_encrypt.additionalSubDomain" ""

echo "CONFIG_ENABLE_AUTORENEW: $CONFIG_ENABLE_AUTORENEW"
echo "EXECUTE_CERTBOT_CMD:     $EXECUTE_CERTBOT_CMD"
echo "EMAIL_ADDR:              $EMAIL_ADDR"
echo "ADDITIONAL_SUBDOMAIN:    $ADDITIONAL_SUBDOMAIN"

## make sure certbot is installed
HAS_CERTBOT_INSTALLED="$(which certbot)"

if [[ -z "${HAS_CERTBOT_INSTALLED}" ]] ; then
  echo "Certbot not installed"
  EXECUTE_CERTBOT_CMD="false"
else
  echo "Certbot is installed     ${HAS_CERTBOT_INSTALLED}"
fi


HAS_APACHE_ROOTDOMAIN_CONF=""
ROOTDOMAIN_HTTP_CONF_FILE="/etc/httpd/conf.d/${THISDOMAINNAME}.conf"

if [[ -e "${ROOTDOMAIN_HTTP_CONF_FILE}" ]] ; then
  echo "Found existing Apache root domain .conf file "
  HAS_APACHE_ROOTDOMAIN_CONF="true"
fi


## fetch previously registered domain names
DOMAIN_NAME_LIST=""
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"

echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "Found domain-name-list:  ${DOMAIN_NAME_LIST}"

echo "Downloading Mattermost server binary from releases.mattermost.com"
VERSION="$(curl -s https://api.github.com/repos/mattermost/mattermost-server/releases/latest | grep tag_name | cut -d '"' -f 4 | sed s/^v//)"
echo "Latest version:          $VERSION"

## for example: https://releases.mattermost.com/5.27.0/mattermost-5.27.0-linux-amd64.tar.gz
echo "    wget -q -O mattermost.tar.gz https://releases.mattermost.com/${VERSION}/mattermost-${VERSION}-linux-amd64.tar.gz"

cd /usr/local/pbase-data/pbase-mattermost
wget -q -O mattermost.tar.gz https://releases.mattermost.com/${VERSION}/mattermost-${VERSION}-linux-amd64.tar.gz

echo "Downloaded file:"
ls -lh mattermost.tar.gz
chown root:root mattermost.tar.gz

echo "Installing in directory: /opt/mattermost"
tar zxf mattermost.tar.gz -C /opt

mkdir /opt/mattermost/data

echo "Creating group and user: mattermost"
useradd -U -M -d /opt/mattermost mattermost

chown -R mattermost:mattermost /opt/mattermost
chmod -R g+w /opt/mattermost

/bin/cp --no-clobber /opt/mattermost/config/config.json /opt/mattermost/config/config.json-ORIG

## sample after editing the config file's datasource line
##   "SqlSettings": {
##       "DriverName": "mysql",
##       "DataSource": "mysql://mmuser:shomeddata@tcp(localhost:3306)/mattermost?charset=utf8mb4,utf8\u0026readTimeout=30s\u0026writeTimeout=30s",

##   "SqlSettings": {
##     "DriverName": "postgres",
##     "DataSource": "postgres://mmuser:mostest@localhost/mattermost_test?sslmode=disable\u0026connect_timeout=10",

echo "Updating config:         /opt/mattermost/config/config.json"
echo "Enabling service:        /etc/systemd/system/mattermost"

/bin/cp --no-clobber /usr/local/pbase-data/pbase-mattermost/etc-systemd-system/mattermost.service /etc/systemd/system/
chmod 664 /etc/systemd/system/mattermost.service

/bin/cp --no-clobber /opt/mattermost/config/config.json /opt/mattermost/config/config.json-ORIG

if [[ $PBASE_CONFIG_NAME == "pbase_postgres" ]] ; then
  echo "Setting Postgres connection"
  sed -i -e "s/mysqld.service/postgresql.service/" /etc/systemd/system/mattermost.service

  sed -i -e "s/mysql/postgres/" /opt/mattermost/config/config.json
  sed -i -e "s/\"mmuser/\"postgres:\/\/mmuser/" /opt/mattermost/config/config.json
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
  sed -i -e "s/postgres/mysql/" /opt/mattermost/config/config.json
  sed -i -e "s/mmuser/$CONFIG_DB_USER/" /opt/mattermost/config/config.json
  sed -i -e "s/mostest/$CONFIG_DB_PSWD/" /opt/mattermost/config/config.json
  sed -i -e "s/mattermost_test/$CONFIG_DB_NAME/" /opt/mattermost/config/config.json
fi


systemctl daemon-reload
systemctl enable mattermost

echo "Starting service:        /etc/systemd/system/mattermost"
systemctl start mattermost
systemctl status mattermost


## add shell aliases
append_bashrc_alias journalmattermost "journalctl -u mattermost -f"
append_bashrc_alias tailmattermost "tail -f /opt/mattermost/logs/mattermost.log"
append_bashrc_alias editmattermostconf "vi /opt/mattermost/config/config.json"

append_bashrc_alias stopmattermost "/bin/systemctl stop mattermost"
append_bashrc_alias startmattermost "/bin/systemctl start mattermost"
append_bashrc_alias statusmattermost "/bin/systemctl status mattermost"
append_bashrc_alias restartmattermost "/bin/systemctl restart mattermost"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

if [[ ${URL_SUBDOMAIN} == "" ]] || [[ ${URL_SUBDOMAIN} == null ]] ; then
  FULLDOMAINNAME="${THISDOMAINNAME}"
  echo "Using root domain:       ${FULLDOMAINNAME}"
else
  FULLDOMAINNAME="${URL_SUBDOMAIN}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi


DOMAIN_NAME_LIST_NEW=""
DOMAIN_NAME_PARAM=""

if [[ "${DOMAIN_NAME_LIST}" == "" ]] ; then
  DOMAIN_NAME_LIST_NEW="${FULLDOMAINNAME}"
  DOMAIN_NAME_PARAM="${FULLDOMAINNAME}"
else
    ## use cut to grab first name from comma delimited list
    FIRSTDOMAINNREGISTERED=$(cut -f1 -d "," ${SAVE_CMD_DIR}/domain-name-list.txt)
    echo "FIRSTDOMAINNREGISTERED:  ${FIRSTDOMAINNREGISTERED}"

  if [[ "${DOMAIN_NAME_LIST}" == *"${FULLDOMAINNAME}"* ]]; then
    echo "Already has ${FULLDOMAINNAME}"
    DOMAIN_NAME_LIST_NEW="${DOMAIN_NAME_LIST}"
    DOMAIN_NAME_PARAM="${DOMAIN_NAME_LIST}"
  else
    echo "Adding ${FULLDOMAINNAME}"
    DOMAIN_NAME_LIST_NEW="${DOMAIN_NAME_LIST},${FULLDOMAINNAME}"
    DOMAIN_NAME_PARAM="${DOMAIN_NAME_LIST},${FULLDOMAINNAME} --expand"
  fi
fi

echo "${DOMAIN_NAME_LIST_NEW}" > ${SAVE_CMD_DIR}/domain-name-list.txt
echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"


echo "FULLDOMAINNAME:          $FULLDOMAINNAME"
echo "SUBPATH_URI:             $SUBPATH_URI"
echo "PROXY_CONF_FILE:         $PROXY_CONF_FILE"

if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  ## must install apache first
  if [[ ! -d "/etc/httpd/conf.d/" ]] ; then
    echo "Apache not found:        /etc/httpd/conf.d/"
    exit 0
  fi

  PREV_CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  if [[ -e "${PREV_CONF_FILE}" ]] ; then
    echo "Disabling previous:      ${PREV_CONF_FILE}"
    mv "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf-DISABLED"
  fi

MATTERMOST_READY_MSG="Next Step - required open this URL to complete install"

if [[ "$URL_SUBDOMAIN" != "" ]] && [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  PROXY_CONF="/etc/httpd/conf.d/mattermost-proxy-subdomain.conf"
  PROXY_CONF_FULLDOMAINNAME="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

  echo "Adding ${URL_SUBDOMAIN} subdomain proxy to mattermost application"

  /bin/cp --no-clobber /usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy-subdomain.conf /etc/httpd/conf.d/

  sed -i "s/mysubdomain.mydomain.com/${FULLDOMAINNAME}/" $PROXY_CONF
  sed -i "s/hostmaster@mydomain.com/${APACHE_SERVER_ADMIN}/" $PROXY_CONF

  echo "Configured Apache proxy:   ${PROXY_CONF_FULLDOMAINNAME}"
  mv "{$PROXY_CONF}" "${PROXY_CONF_FULLDOMAINNAME}"

  systemctl daemon-reload
  systemctl restart httpd

  ## LETS ENCRYPT - HTTPS CERTIFICATE
  echo ""
  CERTBOT_CMD="certbot --apache --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"

  ## save command line in file
  echo "Saving command line:     ${SAVE_CMD_DIR}/certbot-cmd.sh"
  echo ${CERTBOT_CMD} > ${SAVE_CMD_DIR}/certbot-cmd.sh

  if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
    echo "Executing:               ${CERTBOT_CMD}"
    eval "${CERTBOT_CMD}"
  else
    echo "Skipping execute:        EXECUTE_CERTBOT_CMD=false"
    echo "                         ${CERTBOT_CMD}"
  fi

  echo "$MATTERMOST_READY_MSG"
  echo "                         http://${FULLDOMAINNAME}/install"
  echo "  or"
  echo "                         http://localhost/install"
elif [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  echo "Adding / proxy to mattermost"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy.conf /etc/httpd/conf.d/
  PROXY_CONF="/etc/httpd/conf.d/mattermost-proxy.conf"

  echo "Updating config file:    ${PROXY_CONF}"
  sed -i "s/mydomain.com/${THISDOMAINNAME}/" $PROXY_CONF
  systemctl daemon-reload
  systemctl restart httpd

  echo "$MATTERMOST_READY_MSG"
  echo "                         http://${THISDOMAINNAME}/install"
  echo "  or"
  echo "                         http://localhost/install"
else
  echo "$MATTERMOST_READY_MSG"
  echo "                         http://${THISDOMAINNAME}:8065/install"
  echo "  or"
  echo "                         http://localhost:8065/install"
fi


  echo "Mattermost service running. Open this URL to complete install."
  echo "                         http://${FULLDOMAINNAME}${SUBPATH_URI}/install"
fi

echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-mattermost/etc-systemd-system/mattermost.service
/usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy.conf
/usr/local/pbase-data/pbase-mattermost/root-uri/etc-httpd-confd/mattermost-proxy-subdomain.conf
