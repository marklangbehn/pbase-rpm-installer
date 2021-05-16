Name: pbase-gitea
Version: 1.0
Release: 1
Summary: PBase Gitea service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-gitea-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-gitea
Requires: pbase-apache, git, curl, xz, jq

%description
PBase Gitea service

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
  ## name of config file is passed in param $1 - for example "pbase_gitea.json"
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

echo "PBase Gitea service"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## check if already installed
if [[ -d "/var/lib/gitea" ]]; then
  echo "/var/lib/gitea directory already exists - exiting"
  exit 0
fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## Gitea config
## look for config file "pbase_gitea.json"
PBASE_CONFIG_FILENAME="pbase_gitea.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
## version to download
parseConfig "GITEA_VER_CONFIG" ".pbase_gitea.giteaVersion" ""

parseConfig "HTTP_PORT" ".pbase_gitea.httpPort" "3000"
parseConfig "ADD_APACHE_PROXY" ".pbase_gitea.addApacheProxy" "false"
parseConfig "DATABASE" ".pbase_gitea.database" "postgres"
parseConfig "URL_SUBPATH" ".pbase_gitea.urlSubPath" ""

echo "HTTP_PORT:               $HTTP_PORT"
echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"
echo "DATABASE:                $DATABASE"
echo "URL_SUBPATH:             $URL_SUBPATH"


## look for config file "pbase_apache.json"
PBASE_CONFIG_FILENAME="pbase_apache.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"
parseConfig "ENABLE_CHECK_FOR_WWW" ".pbase_apache.enableCheckForWww" "true"

echo "ENABLE_CHECK_FOR_WWW:    $ENABLE_CHECK_FOR_WWW"


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

echo "Downloading Gitea server binary from gitea.io"

if [[ ${GITEA_VER_CONFIG} != "" ]]; then
  VERSION="${GITEA_VER_CONFIG}"
  echo "Configured version:      $GITEA_VER_CONFIG"
else
  VERSION="$(curl -s https://api.github.com/repos/go-gitea/gitea/releases/latest | grep tag_name | cut -d '"' -f 4 | sed s/^v//)"
  echo "Latest version:          $VERSION"
fi

DOWNLOAD_URL="https://github.com/go-gitea/gitea/releases/download/v${VERSION}/gitea-${VERSION}-linux-amd64.xz"

echo "Github DOWNLOAD_URL:     $DOWNLOAD_URL"

cd /usr/local/pbase-data/pbase-gitea
/bin/rm -f gitea*

echo "Downloading:             curl $DOWNLOAD_URL --output gitea.xz --silent"
curl -L $DOWNLOAD_URL --output gitea.xz --silent

echo "Unzipping:               gitea.xz"
xz --decompress gitea.xz

chmod +x gitea
mv /usr/local/pbase-data/pbase-gitea/gitea /usr/local/bin/

echo "Downloaded file from gitea.io:"
ls -l /usr/local/bin/gitea

echo "Creating group and user: git"

adduser \
   --system \
   --shell /bin/bash \
   --comment 'Git Version Control' \
   --user-group \
   --home /home/git -m \
   git


echo "Creating directories:    /var/lib/gitea"
echo "                         /etc/gitea"

mkdir -p /var/lib/gitea/{custom,data,indexers,log}

chown git:git /var/lib/gitea/{custom,data,indexers,log}
chmod 750 /var/lib/gitea/{custom,data,indexers,log}

mkdir /etc/gitea
chown root:git /etc/gitea
chmod 770 /etc/gitea

echo "Setting permission:      chown git:git /etc/gitea/app.ini"
touch /etc/gitea/app.ini
chown git:git /etc/gitea/app.ini


## when DB_PSWD is populated below that means DB config has been defined
DB_PSWD=""

if [[ $DATABASE == "postgres" ]]; then
  PBASE_CONFIG_FILENAME="pbase_postgres.json"
  locateConfigFile "$PBASE_CONFIG_FILENAME"
  parseConfig "DB_HOSTNAME" ".pbase_postgres[0].default.hostName" "localhost"
  parseConfig "DB_PORT"     ".pbase_postgres[0].default.port" "5432"
  parseConfig "DB_NAME"     ".pbase_postgres[0].default.database[0].name" "gitea"
  parseConfig "DB_USER"     ".pbase_postgres[0].default.database[0].user" "gitea"
  parseConfig "DB_CHARSET"  ".pbase_postgres[0].default.database[0].characterSet" "UTF8"
  parseConfig "DB_PSWD"     ".pbase_postgres[0].default.database[0].password" ""

elif [[ $DATABASE == "mysql" ]]; then
  PBASE_CONFIG_FILENAME="pbase_mysql.json"
  locateConfigFile "$PBASE_CONFIG_FILENAME"
  parseConfig "DB_HOSTNAME" ".pbase_mysql[0].default.hostName" "localhost"
  parseConfig "DB_PORT"     ".pbase_mysql[0].default.port" "3306"
  parseConfig "DB_NAME"     ".pbase_mysql[0].default.database[0].name" "gitea"
  parseConfig "DB_USER"     ".pbase_mysql[0].default.database[0].user" "gitea"
  parseConfig "DB_CHARSET"  ".pbase_mysql[0].default.characterSet" "utf8mb48"
  parseConfig "DB_PSWD"     ".pbase_mysql[0].default.database[0].password" ""
fi

## add DB config to app.ini
if [[ $DB_PSWD != "" ]]; then
  echo "Setting Gitea database:  /etc/gitea/app.ini"
  echo "DB_TYPE  = ${DATABASE}"
  echo "HOST     = ${DB_HOSTNAME}:${DB_PORT}"
  echo "NAME     = ${DB_NAME}"
  echo "USER     = ${DB_USER}"
  echo "PASSWD   = ${DB_PSWD}"
  echo "CHARSET  = ${DB_CHARSET}"

  echo "" >> "/etc/gitea/app.ini"
  echo "[database]" >> "/etc/gitea/app.ini"
  echo "DB_TYPE  = ${DATABASE}" >> "/etc/gitea/app.ini"
  echo "HOST     = ${DB_HOSTNAME}:${DB_PORT}" >> "/etc/gitea/app.ini"
  echo "NAME     = ${DB_NAME}" >> "/etc/gitea/app.ini"
  echo "USER     = ${DB_USER}" >> "/etc/gitea/app.ini"
  echo "PASSWD   = ${DB_PSWD}" >> "/etc/gitea/app.ini"
  echo "SCHEMA   = "           >> "/etc/gitea/app.ini"
  echo "SSL_MODE = disable"    >> "/etc/gitea/app.ini"
  echo "CHARSET  = ${DB_CHARSET}" >> "/etc/gitea/app.ini"
fi

## configure systemd service file depending on database type
if [[ $DATABASE == "postgres" ]]; then
  cp --no-clobber /usr/local/pbase-data/pbase-gitea/etc-systemd-system/postgres/gitea.service /etc/systemd/system/
else
  cp --no-clobber /usr/local/pbase-data/pbase-gitea/etc-systemd-system/mysql/gitea.service /etc/systemd/system/
fi

if [[ $DATABASE == "" ]]; then
  ## when database config is blank that means comment out the line: 'After=mysql'
  sed -i -e "s/After=mysqld.service/#After=mysqld.service/" /etc/systemd/system/gitea.service
fi


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
HAS_WWW_SUBDOMAIN="false"
DOMAIN_NAME_LIST=""
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"

echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "Found domain-name-list:  ${DOMAIN_NAME_LIST}"

## configure SMTP email
PBASE_CONFIG_FILENAME="pbase_smtp.json"
PBASE_CONFIG_NAME="pbase_smtp"
locateConfigFile "$PBASE_CONFIG_FILENAME"
SMTP_PASSWORD=""

if [[ -e "/usr/local/pbase-data/admin-only/module-config.d/pbase_smtp.json" ]] ; then
  parseConfig "SMTP_SERVER" ".${PBASE_CONFIG_NAME}.server" "smtp.mailgun.org"
  parseConfig "SMTP_PORT" ".${PBASE_CONFIG_NAME}.port" "587"
  parseConfig "SMTP_LOGIN" ".${PBASE_CONFIG_NAME}.login" "postmaster@mail.${THISDOMAINNAME}"
  parseConfig "SMTP_PASSWORD" ".${PBASE_CONFIG_NAME}.password" ""
  parseConfig "SMTP_AUTH_METHOD" ".${PBASE_CONFIG_NAME}.authMethod" "plain"
  parseConfig "SMTP_OPENSSL_VERIFY_MODE" ".${PBASE_CONFIG_NAME}.openSSLVerifyMode" "none"
fi


if [[ "$SMTP_PASSWORD" == "" ]] ; then
  echo "No SMTP password given:  pbase_smtp.json"
else
  echo "Setting SMTP config:     /etc/gitea/app.ini"
  echo "SMTP_SERVER:             $SMTP_SERVER"
  echo "SMTP_PORT:               $SMTP_PORT"
  echo "SMTP_LOGIN:              $SMTP_LOGIN"
  echo "SMTP_PASSWORD:           $SMTP_PASSWORD"
  #echo "SMTP_AUTH_METHOD:        $SMTP_AUTH_METHOD"
  #echo "SMTP_OPENSSL_VERIFY_MODE:$SMTP_OPENSSL_VERIFY_MODE"

  echo "" >> "/etc/gitea/app.ini"
  echo "[mailer]" >> "/etc/gitea/app.ini"
  echo "ENABLED = true" >> "/etc/gitea/app.ini"
  echo "HOST    = ${SMTP_SERVER}:${SMTP_PORT}" >> "/etc/gitea/app.ini"
  echo "FROM    = noreply@${THISDOMAINNAME}"   >> "/etc/gitea/app.ini"
  echo "USER    = ${SMTP_LOGIN}"    >> "/etc/gitea/app.ini"
  echo "PASSWD  = ${SMTP_PASSWORD}" >> "/etc/gitea/app.ini"
fi


## check for subdomain
FULLDOMAINNAME="$THISDOMAINNAME"

## for Apache config choose either the ...subpath.conf or the ...subdomain.conf
##   depending on URL_SUBPATH and URL_SUBDOMAIN

PROXY_CONF_FILE="gitea-proxy-subpath.conf"
SUBPATH_URI=""

if [[ ${URL_SUBPATH} != "" ]] ; then
  SUBPATH_URI="/${URL_SUBPATH}"
  echo "Using SUBPATH_URI:       $SUBPATH_URI"
else
  PROXY_CONF_FILE="gitea-proxy-subdomain.conf"
  if [[ ${URL_SUBDOMAIN} == "" ]] || [[ ${URL_SUBDOMAIN} == null ]] ; then
    FULLDOMAINNAME="${THISDOMAINNAME}"
    echo "Using root domain:       ${FULLDOMAINNAME}"
  else
    FULLDOMAINNAME="${URL_SUBDOMAIN}.${THISDOMAINNAME}"
    echo "Using subdomain:         ${FULLDOMAINNAME}"
  fi
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

  /bin/cp --no-clobber /usr/local/pbase-data/pbase-gitea/etc-httpd-confd/${PROXY_CONF_FILE} /etc/httpd/conf.d/

  mv "/etc/httpd/conf.d/${PROXY_CONF_FILE}" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

  if [[ ${URL_SUBDOMAIN} != "" ]] ; then
    echo "Setting subdomain:       ${CONF_FILE}"
    sed -i -e "s/git.example.com/${FULLDOMAINNAME}/" "${CONF_FILE}"
  else
    if [[ ${URL_SUBPATH} != "git" ]] ; then
      echo "Setting subpath:         ${CONF_FILE}"
      sed -i -e "s/git.example.com/${FULLDOMAINNAME}/" "${CONF_FILE}"
      sed -i -e "s|/git http|/${URL_SUBPATH} http|" "${CONF_FILE}"
    fi
  fi

  echo "Gitea server config:     /etc/gitea/app.ini"
  echo "" >> "/etc/gitea/app.ini"
  echo "[server]" >> "/etc/gitea/app.ini"
  echo "ROOT_URL = http://${FULLDOMAINNAME}${SUBPATH_URI}/" >> "/etc/gitea/app.ini"

  echo ""
  echo "Starting service:        /etc/systemd/system/gitea"
  systemctl daemon-reload
  systemctl enable gitea

  systemctl start gitea
  systemctl status gitea

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

  echo "Gitea service running. Open this URL to complete install."
  echo "                         http://${FULLDOMAINNAME}${SUBPATH_URI}/install"
else
  echo "Starting service:        /etc/systemd/system/gitea"
  systemctl daemon-reload
  systemctl enable gitea
  systemctl start gitea
  systemctl status gitea

  echo "Gitea service running. Open this URL to complete install."
  echo "                         http://localhost:3000/install"
fi

## add shell aliases
append_bashrc_alias editgiteaconf "vi /etc/gitea/app.ini"
append_bashrc_alias stopgitea "/bin/systemctl stop gitea"
append_bashrc_alias startgitea "/bin/systemctl start gitea"
append_bashrc_alias statusgitea "/bin/systemctl status gitea"
append_bashrc_alias restartgitea "/bin/systemctl restart gitea"
append_bashrc_alias tailgitea "journalctl -xf -u gitea"
## append_bashrc_alias tailgitea "tail -f /var/lib/gitea/log/gitea.log"


echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-gitea/etc-httpd-confd/gitea-proxy-subdomain.conf
/usr/local/pbase-data/pbase-gitea/etc-httpd-confd/gitea-proxy-subpath.conf
/usr/local/pbase-data/pbase-gitea/etc-systemd-system/mysql/gitea.service
/usr/local/pbase-data/pbase-gitea/etc-systemd-system/postgres/gitea.service
