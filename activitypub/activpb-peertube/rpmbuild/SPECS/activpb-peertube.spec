Name: activpb-peertube
Version: 1.0
Release: 2
Summary: PBase Peertube service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: activpb-peertube-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: activpb-peertube
Requires: nginx, postgresql, openssl, gcc-c++, make, wget, redis, git, ffmpeg, nodejs, unzip, yarn, certbot, jq, python3-pip

%description
PBase Peertube ActivityPub service

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
  ## name of config file is passed in param $1 - for example "activpb_peertube.json"
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

echo "PBase Peertube ActivityPub server install"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## check if already installed
if [[ -e "/var/www/peertube/config/production.yaml" ]]; then
  echo "/var/www/peertube/config/production.yaml already exists - exiting"
  exit 0
fi

## check if node 12 or higher installed
VERS_INSTALLED="$(node --version)"
VERS_REQUIRED="v12.0.0"

if [ "$(printf '%s\n' "$VERS_REQUIRED" "$VERS_INSTALLED" | sort -V | head -n1)" = "$VERS_REQUIRED" ]; then
  echo "Node JS version:         ${VERS_INSTALLED}"
  echo ""
else
  echo "Less than ${VERS_REQUIRED}"
  echo "Node JS version 12 or higher required, found: ${VERS_INSTALLED}"
  echo "Exiting."
  exit 0
fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## Peertube config
## look for config file "activpb_peertube.json"
PBASE_CONFIG_FILENAME="activpb_peertube.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
## version to download
parseConfig "PEERTUBE_VER_CONFIG" ".activpb_peertube.peertubeVersion" ""

parseConfig "HTTP_PORT" ".activpb_peertube.port" "9000"
parseConfig "ADD_NGINX_PROXY" ".activpb_peertube.addNgnixProxy" "true"
parseConfig "ADD_APACHE_PROXY" ".activpb_peertube.addApacheProxy" ""
parseConfig "URL_SUBDOMAIN" ".activpb_peertube.urlSubDomain" "peertube"

echo "HTTP_PORT:               $HTTP_PORT"
echo "ADD_NGINX_PROXY:         $ADD_NGINX_PROXY"
echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"
echo "URL_SUBDOMAIN:           $URL_SUBDOMAIN"


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"


## Database config
PBASE_CONFIG_FILENAME="pbase_postgres.json"
PBASE_CONFIG_NAME="pbase_postgres"

echo "PBASE_CONFIG_FILENAME:   $PBASE_CONFIG_FILENAME"
##echo "PBASE_CONFIG_NAME:       $PBASE_CONFIG_NAME"

locateConfigFile "${PBASE_CONFIG_FILENAME}"

## fetch config value from JSON file

parseConfig "CONFIG_DB_HOSTNAME" ".${PBASE_CONFIG_NAME}[0].default.hostName" "localhost"
parseConfig "CONFIG_DB_PORT"     ".${PBASE_CONFIG_NAME}[0].default.port" "5432"
parseConfig "CONFIG_DB_CHARSET"  ".${PBASE_CONFIG_NAME}[0].default.database[0].characterSet" "UTF8"

parseConfig "CONFIG_DB_STARTSVC" ".${PBASE_CONFIG_NAME}[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".${PBASE_CONFIG_NAME}[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".${PBASE_CONFIG_NAME}[0].default.database[0].name" "peertube_prod"
parseConfig "CONFIG_DB_USER"     ".${PBASE_CONFIG_NAME}[0].default.database[0].user" "peertube"
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

## Outgoing SMTP config
PBASE_CONFIG_FILENAME="pbase_smtp.json"
PBASE_CONFIG_NAME="pbase_smtp"

echo ""
echo "PBASE_CONFIG_FILENAME:   $PBASE_CONFIG_FILENAME"
##echo "PBASE_CONFIG_NAME:       $PBASE_CONFIG_NAME"

locateConfigFile "${PBASE_CONFIG_FILENAME}"

## fetch config values from JSON file
parseConfig "SMTP_SERVER" ".${PBASE_CONFIG_NAME}.server" "smtp.mailgun.org"
parseConfig "SMTP_PORT" ".${PBASE_CONFIG_NAME}.port" "587"
parseConfig "SMTP_LOGIN" ".${PBASE_CONFIG_NAME}.login" "postmaster@mail.${THISDOMAINNAME}"
parseConfig "SMTP_PASSWORD" ".${PBASE_CONFIG_NAME}.password" "mysmtppassword"
parseConfig "SMTP_AUTH_METHOD" ".${PBASE_CONFIG_NAME}.authMethod" "plain"
parseConfig "SMTP_OPENSSL_VERIFY_MODE" ".${PBASE_CONFIG_NAME}.openSSLVerifyMode" "none"

echo "SMTP_SERVER:             $SMTP_SERVER"
echo "SMTP_PORT:               $SMTP_PORT"
echo "SMTP_LOGIN:              $SMTP_LOGIN"
echo "SMTP_PASSWORD:           $SMTP_PASSWORD"
echo "SMTP_AUTH_METHOD:        $SMTP_AUTH_METHOD"
echo "SMTP_OPENSSL_VERIFY_MODE:$SMTP_OPENSSL_VERIFY_MODE"


## REDIS
echo ""
echo "Starting redis service"
systemctl daemon-reload
systemctl enable redis

systemctl start redis
systemctl status redis


## symlink for python3 to python
ln -s /usr/bin/python3 /usr/bin/python


## POSTGRES
echo "Enable Postgres extensions used by PeerTube"
echo "                         psql -c 'CREATE EXTENSION pg_trgm;' $CONFIG_DB_NAME"
echo "                         psql -c 'CREATE EXTENSION unaccent;' $CONFIG_DB_NAME"

su - postgres -c "psql -c 'CREATE EXTENSION pg_trgm;' $CONFIG_DB_NAME"
su - postgres -c "psql -c 'CREATE EXTENSION unaccent;' $CONFIG_DB_NAME"


## USER
echo "Creating group and user: peertube"
mkdir -p /var/www/

adduser \
   --system \
   --shell /bin/bash \
   --comment 'Peertube service' \
   --user-group \
   --home /var/www/peertube -m \
   peertube

## make sub-directories
cd /var/www/peertube/
mkdir config storage versions

## DOWNLOAD CODE

## download yq binary from: https://mikefarah.gitbook.io/yq/
cd /usr/local/bin
wget -q -O yq "https://github.com/mikefarah/yq/releases/download/3.2.3/yq_linux_amd64"
chmod +x yq

echo "Yaml editor utility:     yq"
ls -l /usr/local/bin/yq


## download peertube package from github
cd /var/www/peertube/versions
echo "Downloading Peertube"

if [[ "${PEERTUBE_VER_CONFIG}" != "" ]]; then
  VERSION="${PEERTUBE_VER_CONFIG}"
  echo "Configured version:      $PEERTUBE_VER_CONFIG"
else
  VERSION=$(curl -s https://api.github.com/repos/chocobozzz/peertube/releases/latest | grep tag_name | cut -d '"' -f 4)
  echo "Latest version:          $VERSION"
fi

wget -q "https://github.com/Chocobozzz/PeerTube/releases/download/${VERSION}/peertube-${VERSION}.zip"

echo "Unzipping peertube package"
ls -l peertube-${VERSION}.zip

unzip -q peertube-${VERSION}.zip
/bin/rm -f peertube-${VERSION}.zip

## symlink
cd /var/www/peertube/
ln -s versions/peertube-${VERSION} peertube-latest

## set ownership
chown -R peertube:peertube /var/www/peertube

## nginx needs +x permission on parent dir
chmod +x /var/www/peertube


## run install
echo ""
echo "Executing:               yarn install --silent --production --pure-lockfile"
su - peertube -c "cd /var/www/peertube/peertube-latest/ && yarn install --silent --production --pure-lockfile"

## copy example config file
echo ""
echo "Peertube config:         /var/www/peertube/config/production.yaml"
su - peertube -c "cp /var/www/peertube/peertube-latest/config/production.yaml.example /var/www/peertube/config/production.yaml"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

## FIRSTDOMAINNREGISTERED should match the subdirectory under /etc/letsencrypt/live
FIRSTDOMAINNREGISTERED="${FULLDOMAINNAME}"

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
echo "                         ${DOMAIN_NAME_LIST_NEW}"
echo ""

DOMAIN_NAME_LIST_HAS_WWW=$(grep www ${SAVE_CMD_DIR}/domain-name-list.txt)
##echo "Domain list has WWW:     ${DOMAIN_NAME_LIST_HAS_WWW}"

echo "Updating config in production.yaml"

/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml webserver.hostname "${FULLDOMAINNAME}"
/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml listen.port "${HTTP_PORT}"

/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml database.username "${CONFIG_DB_USER}"
/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml database.password "${CONFIG_DB_PSWD}"

/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml smtp.hostname "${SMTP_SERVER}"
/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml smtp.port "${SMTP_PORT}"
/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml smtp.username "${SMTP_LOGIN}"
/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml smtp.password "${SMTP_PASSWORD}"

/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml smtp.tls "false"
/usr/local/bin/yq w -i /var/www/peertube/config/production.yaml smtp.from_address "admin@${THISDOMAINNAME}"

## set permissions on config file
chown peertube:peertube /var/www/peertube/config/production.yaml
chmod 0600 /var/www/peertube/config/production.yaml

## 3.0 template substitution
## variables to be substituted in nginx conf.d file
export WEBSERVER_HOST="${FULLDOMAINNAME}"
export PEERTUBE_HOST="localhost"
envsubst '${WEBSERVER_HOST},${PEERTUBE_HOST}' < /var/www/peertube/peertube-latest/support/nginx/peertube > /etc/nginx/conf.d/peertube.conf

## how enable aio on nginx? turn off 'aio threads' for now
sed -i "s/aio threads/##aio threads/g" /etc/nginx/conf.d/peertube.conf


## replace proxy_pass backend with:  http://127.0.0.1:9000
sed -i "s|proxy_pass http://backend|proxy_pass http://127.0.0.1:9000|g" /etc/nginx/conf.d/peertube.conf

if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  mv /etc/nginx/conf.d/peertube.conf /usr/local/pbase-data/activpb-peertube/peertube.conf-NGINX-DISABLED

  ## set aside conf file so that certbot can recreate the ...le-ssl.conf
  if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" ]] ; then
    echo "Disabling prev conf:     /etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf"
    mv "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf-DISABLED"
  fi

  ## configure apache proxy file
  echo "Apache virtual host:     /etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  /bin/cp -f "/usr/local/pbase-data/activpb-peertube/etc-httpd-conf-d/peertube.example.com.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  sed -i "s/peertube.example.com/${FULLDOMAINNAME}/g" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

  ## may also enable www alias
  echo "Check for www alias"
  sed -i "s/www.example.com/www.${THISDOMAINNAME}/" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

  if [[ "${DOMAIN_NAME_LIST_HAS_WWW}" != "" ]] ; then
    echo "Enabling:                ServerAlias www.${THISDOMAINNAME}"
    sed -i "s/#ServerAlias/ServerAlias/" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  fi

  mkdir -p "/etc/httpd/logs/${FULLDOMAINNAME}"
  systemctl reload httpd

else
  echo "Configuration updated:   /etc/nginx/conf.d/peertube.conf"
  echo "Nginx configuration:     /etc/nginx/conf.d/"
  ls -l /etc/nginx/conf.d/
fi


## LETS ENCRYPT - HTTPS CERTIFICATE
echo ""

if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  ## APACHE
  CERTBOT_CMD="certbot --apache --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"
else
  ## NGINX
  CERTBOT_CMD="certbot certonly --standalone --post-hook 'systemctl start nginx' --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"
fi

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


EXTERNALURL="https://$FULLDOMAINNAME"
echo "URL:                     $EXTERNALURL"


## CRON

if [[ $CONFIG_ENABLE_AUTORENEW == "true" ]]; then
  echo "Adding cron jobs:        /etc/crontab"

  ## create empty log file
  CRONJOB_LOGFILE="/var/log/letsencrypt-sslrenew.log"

  touch "$CRONJOB_LOGFILE"
  chown root:root ${CRONJOB_LOGFILE}

  ## run tasks at random minute - under 0:50, random hour before 11pm

  RAND_MINUTE="$((2 + RANDOM % 50))"
  RAND_HOUR="$((2 + RANDOM % 23))"

  if [[ "$ADD_NGINX_PROXY" == "true" ]] ; then
    CRONJOB_LINE1="${RAND_MINUTE} ${RAND_HOUR} * * * root /usr/bin/certbot renew --deploy-hook '/bin/systemctl reload nginx' >> $CRONJOB_LOGFILE"
  fi

  if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
    CRONJOB_LINE1="${RAND_MINUTE} ${RAND_HOUR} * * * root /usr/bin/certbot renew --deploy-hook '/bin/systemctl reload httpd' >> $CRONJOB_LOGFILE"
  fi

  echo ""  >>  /etc/crontab
  echo "## Added by activpb-peertube RPM ##"  >>  /etc/crontab
  echo "$CRONJOB_LINE1"  >>  /etc/crontab
else
  echo "Crontab unchanged:       enableAutoRenew=false"
fi


## Add aliases helpful for admin tasks to .bashrc
echo ""
echo "" >> /root/.bashrc
append_bashrc_alias tailpeertube "journalctl -feu peertube"

append_bashrc_alias statuspeertube "systemctl status peertube"
append_bashrc_alias stoppeertube "systemctl stop peertube"
append_bashrc_alias startpeertube "systemctl start peertube"
append_bashrc_alias restartpeertube "systemctl restart peertube"

append_bashrc_alias editpeertubeconf "vi /var/www/peertube/config/production.yaml"

if [[ "$ADD_NGINX_PROXY" == "true" ]] ; then
  append_bashrc_alias tailnginx "tail -f /var/log/nginx/*.log"
  append_bashrc_alias editnginxconf "vi /etc/nginx/conf.d/peertube.conf"
  append_bashrc_alias statusnginx "systemctl status nginx"
  append_bashrc_alias stopnginx "systemctl stop nginx"
  append_bashrc_alias startnginx "systemctl start nginx"
  append_bashrc_alias restartnginx "systemctl restart nginx"
fi


echo "TCP/IP Tuning:           /etc/sysctl.d/30-peertube-tcp.conf"
cp /var/www/peertube/peertube-latest/support/sysctl.d/30-peertube-tcp.conf /etc/sysctl.d/
sysctl -p /etc/sysctl.d/30-peertube-tcp.conf

## add peertube service file
/bin/cp -f --no-clobber /var/www/peertube/peertube-latest/support/systemd/peertube.service /etc/systemd/system/
echo ""

## start services
systemctl daemon-reload

if [[ $EXECUTE_CERTBOT_CMD == "false" ]] ; then
  echo "Skipping certbot:      EXECUTE_CERTBOT_CMD=false"
  echo "Not starting peertube service - enabling only"
  systemctl enable peertube

  if [[ "$ADD_NGINX_PROXY" == "true" ]] ; then
    systemctl enable nginx
  fi
  echo "exiting"
  exit 0
fi

if [[ "$ADD_NGINX_PROXY" == "true" ]] ; then
  echo "Starting nginx service"
  systemctl enable nginx

  systemctl start nginx
  systemctl status nginx
fi

echo ""
echo "Starting peertube service"

systemctl enable peertube
systemctl start peertube
systemctl status peertube


## capture journalctl output to file after waiting 20 seconds for peertube to launch
sleep 20
mkdir -p /usr/local/pbase-data/admin-only/activpb-peertube/
journalctl -u peertube > /usr/local/pbase-data/admin-only/activpb-peertube/journalctl-output.txt

## admin only privs
chmod 0600 /usr/local/pbase-data/admin-only/activpb-peertube/
chmod 0600 /usr/local/pbase-data/admin-only/activpb-peertube/journalctl-output.txt

echo "Saving output from:      journalctl -u peertube"
echo "           to file:      /usr/local/pbase-data/admin-only/activpb-peertube/journalctl-output.txt"

grep "User" /usr/local/pbase-data/admin-only/activpb-peertube/journalctl-output.txt
echo ""

echo "Next Step - required - login to your PeerTube instance URL with the"
echo "                         user and password shown by running the command:"
echo "                             journalctl -u peertube | grep User | cut -d: -f8-"
echo "                         then follow the setup dialog."
echo ""

## show username and password that were written to log
grep "User" /usr/local/pbase-data/admin-only/activpb-peertube/journalctl-output.txt | cut -d: -f8-
echo ""

EXTERNALURL="https://$FULLDOMAINNAME"
echo "PeerTube Ready:          $EXTERNALURL"
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/activpb-peertube/etc-nginx-conf-d/peertube.conf
/usr/local/pbase-data/activpb-peertube/etc-httpd-conf-d/peertube.example.com.conf