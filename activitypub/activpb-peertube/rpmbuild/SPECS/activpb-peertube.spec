Name: activpb-peertube
Version: 1.0
Release: 0
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
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/activpb_peertube.json


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

## check if already installed
if [[ -e "/var/www/peertube/config/production.yaml" ]]; then
  echo "/var/www/peertube/config/production.yaml already exists - exiting"
  exit 0
fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## Peertube config
## look for either separate config file "activpb_peertube.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="activpb_peertube.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
## version to download
parseConfig "PEERTUBE_VER_CONFIG" ".activpb_peertube.peertubeVersion" ""

parseConfig "HTTP_PORT" ".activpb_peertube.port" "9000"
parseConfig "ADD_NGINX_PROXY" ".activpb_peertube.addNgnixProxy" "true"
parseConfig "URL_SUB_DOMAIN" ".activpb_peertube.urlSubDomain" "peertube"

echo "HTTP_PORT:               $HTTP_PORT"
##echo "ADD_NGINX_PROXY:         $ADD_NGINX_PROXY"
echo "URL_SUB_DOMAIN:          $URL_SUB_DOMAIN"


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
#echo "ADDITIONAL_SUBDOMAIN:    $ADDITIONAL_SUBDOMAIN"

DASH_D_ADDITIONAL_SUBDOMAIN=""

if [[ $ADDITIONAL_SUBDOMAIN != "" ]] ; then
  DASH_D_ADDITIONAL_SUBDOMAIN="-d $ADDITIONAL_SUBDOMAIN.$THISDOMAINNAME"
fi


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
echo "Downloading Peertube:    $VERSION"

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
echo "Executing:               yarn install --production --pure-lockfile"
su - peertube -c "cd /var/www/peertube/peertube-latest/ && yarn install --production --pure-lockfile"

## copy example config file
echo ""
echo "Peertube config:         /var/www/peertube/config/production.yaml"
su - peertube -c "cp /var/www/peertube/peertube-latest/config/production.yaml.example /var/www/peertube/config/production.yaml"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

if [[ "$URL_SUB_DOMAIN" != "" ]] ; then
  FULLDOMAINNAME="${URL_SUB_DOMAIN}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi

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

## 3.0 preliminary template substitution
## variables to be substituted in nginx conf.d file
#export WEBSERVER_HOST="${FULLDOMAINNAME}"
#export PEERTUBE_HOST="localhost"
#envsubst '${WEBSERVER_HOST},${PEERTUBE_HOST}' < /var/www/peertube/peertube-latest/support/nginx/peertube > /etc/nginx/conf.d/peertube.conf
#
## template cert path changed for v3.0rc
#sed -i "s|peertube/fullchain.pem|${FULLDOMAINNAME}/fullchain.pem|g" /etc/nginx/conf.d/peertube.conf
#sed -i "s|peertube/privkey.pem|${FULLDOMAINNAME}/privkey.pem|g" /etc/nginx/conf.d/peertube.conf
#
##  how enable aio on nginx? turn off 'aio threads' for now
#sed -i "s/aio threads/##aio threads/g" /etc/nginx/conf.d/peertube.conf


## 2.4 template substitution
## /bin/cp -f --no-clobber /var/www/peertube/peertube-latest/support/nginx/peertube /etc/nginx/conf.d/peertube.conf

## replace domain name
/bin/cp -f --no-clobber /usr/local/pbase-data/activpb-peertube/etc-nginx-conf-d/peertube.conf /etc/nginx/conf.d/peertube.conf
sed -i "s/peertube.example.com/${FULLDOMAINNAME}/g" /etc/nginx/conf.d/peertube.conf

echo "Configuration updated:   /etc/nginx/conf.d/peertube.conf"

echo "Nginx configuration:     /etc/nginx/conf.d/"
ls -l /etc/nginx/conf.d/


## LETS ENCRYPT - HTTPS CERTIFICATE
echo ""

if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
  echo "Executing:               certbot certonly --standalone --post-hook "systemctl start nginx" -d ${FULLDOMAINNAME} -m ${EMAIL_ADDR} --agree-tos -n"
  certbot certonly --standalone --post-hook "systemctl start nginx" -d ${FULLDOMAINNAME} -m ${EMAIL_ADDR} --agree-tos -n
else
  echo "Not executing:           certbot certonly --standalone --post-hook "systemctl start nginx" -d ${FULLDOMAINNAME} -m ${EMAIL_ADDR} --agree-tos -n"
  echo "Skipping certbot:        EXECUTE_CERTBOT_CMD=false"
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
  CRONJOB_LINE1="${RAND_MINUTE} ${RAND_HOUR} * * * root /usr/bin/certbot renew --deploy-hook '/bin/systemctl reload nginx' >> $CRONJOB_LOGFILE"

  echo ""  >>  /etc/crontab
  echo "## Added by activpb-peertube RPM ##"  >>  /etc/crontab
  echo "$CRONJOB_LINE1"  >>  /etc/crontab
else
  echo "Crontab unchanged:       enableAutoRenew=false"
fi


## Add aliases helpful for admin tasks to .bashrc
echo ""
echo "" >> /root/.bashrc
append_bashrc_alias tailnginx "tail -f /var/log/nginx/*.log"
append_bashrc_alias tailpeertube "journalctl -feu peertube"

append_bashrc_alias statuspeertube "systemctl status peertube"
append_bashrc_alias stoppeertube "systemctl stop peertube"
append_bashrc_alias startpeertube "systemctl start peertube"
append_bashrc_alias restartpeertube "systemctl restart peertube"

append_bashrc_alias editpeertubeconf "vi /var/www/peertube/config/production.yaml"
append_bashrc_alias editnginxconf "vi /etc/nginx/conf.d/peertube.conf"

append_bashrc_alias statusnginx "systemctl status nginx"
append_bashrc_alias stopnginx "systemctl stop nginx"
append_bashrc_alias startnginx "systemctl start nginx"
append_bashrc_alias restartnginx "systemctl restart nginx"



echo "TCP/IP Tuning:           /etc/sysctl.d/30-peertube-tcp.conf"
cp /var/www/peertube/peertube-latest/support/sysctl.d/30-peertube-tcp.conf /etc/sysctl.d/
sysctl -p /etc/sysctl.d/30-peertube-tcp.conf

## add peertube service file
/bin/cp -f --no-clobber /var/www/peertube/peertube-latest/support/systemd/peertube.service /etc/systemd/system/
echo ""

if [[ $EXECUTE_CERTBOT_CMD == "false" ]] ; then
  echo "Skipping certbot:      EXECUTE_CERTBOT_CMD=false"
  echo "Not starting nginx or peertube service - enabling only"
  systemctl daemon-reload
  systemctl enable nginx
  systemctl enable peertube
  echo "exiting"
  exit 0
fi

echo "Starting nginx service"
systemctl daemon-reload
systemctl enable nginx

systemctl start nginx
systemctl status nginx

echo ""
echo "Starting peertube service"

systemctl enable peertube
systemctl start peertube
systemctl status peertube


## capture journalctl output to file after waiting 15 seconds for peertube to launch
sleep 15
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
