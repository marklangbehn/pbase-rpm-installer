Name: activpb-mastodon
Version: 1.0
Release: 4
Summary: PBase Mastodon service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: activpb-mastodon
Requires: activpb-mastodon-bundle

%description
PBase Mastodon service

%prep

%install

%clean

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
  ## name of config file is passed in param $1 - for example "activpb_mastodon.json"
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

echo "PBase Mastodon server install"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## check if already installed
if [[ -e "/home/mastodon/live/.env.production" ]]; then
  echo "/home/mastodon/live/.env.production already exists - exiting"
  exit 0
fi

## check if node 16 or higher installed
VERS_INSTALLED="$(node --version)"
VERS_REQUIRED="v16.0.0"

if [ "$(printf '%s\n' "$VERS_REQUIRED" "$VERS_INSTALLED" | sort -V | head -n1)" = "$VERS_REQUIRED" ]; then
  echo "Node JS version:         ${VERS_INSTALLED}"
  echo ""
else
  echo "Less than ${VERS_REQUIRED}"
  echo "Node JS version 16 or higher required, found: ${VERS_INSTALLED}"
  echo "Exiting."
  exit 0
fi

## check if home directory has been installed
if [[ ! -d "/home/mastodon" ]]; then
  echo "/home/mastodon directory not found - exiting"
  exit 0
fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## Mastodon config
## look for config file "activpb_mastodon.json"
PBASE_CONFIG_FILENAME="activpb_mastodon.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
## version to download
parseConfig "MASTODON_VER_CONFIG" ".activpb_mastodon.mastodonVersion" ""

parseConfig "HTTP_PORT" ".activpb_mastodon.port" "3000"
parseConfig "ADD_NGINX_PROXY" ".activpb_mastodon.addNgnixProxy" "true"
parseConfig "URL_SUBDOMAIN" ".activpb_mastodon.urlSubDomain" "mastodon"
parseConfig "WEB_DOMAIN_NAME" ".activpb_mastodon.webDomainName" ""
parseConfig "ALTERNATE_DOMAINS" ".activpb_mastodon.alternateDomains" ""
parseConfig "SINGLE_USER_MODE" ".activpb_mastodon.singleUserMode" "false"
parseConfig "AUTHORIZED_FETCH" ".activpb_mastodon.authorizedFetch" "false"
parseConfig "LIMITED_FEDERATION_MODE" ".activpb_mastodon.limitedFederationMode" "false"


echo "HTTP_PORT:               $HTTP_PORT"
##echo "ADD_NGINX_PROXY:         $ADD_NGINX_PROXY"
echo "URL_SUBDOMAIN:           $URL_SUBDOMAIN"
echo "WEB_DOMAIN_NAME:         $WEB_DOMAIN_NAME"
echo "ALTERNATE_DOMAINS:       $ALTERNATE_DOMAINS"
echo "SINGLE_USER_MODE:        $SINGLE_USER_MODE"
echo "AUTHORIZED_FETCH:        $AUTHORIZED_FETCH"
echo "LIMITED_FEDERATION_MODE: $LIMITED_FEDERATION_MODE"


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"


## Database config
PBASE_CONFIG_FILENAME="pbase_postgres.json"
PBASE_CONFIG_NAME="pbase_postgres"

echo "PBASE_CONFIG_FILENAME:   $PBASE_CONFIG_FILENAME"
echo "PBASE_CONFIG_NAME:       $PBASE_CONFIG_NAME"

locateConfigFile "${PBASE_CONFIG_FILENAME}"

## fetch config value from JSON file

parseConfig "CONFIG_DB_HOSTNAME" ".${PBASE_CONFIG_NAME}[0].default.hostName" "localhost"
parseConfig "CONFIG_DB_PORT"     ".${PBASE_CONFIG_NAME}[0].default.port" "5432"
parseConfig "CONFIG_DB_CHARSET"  ".${PBASE_CONFIG_NAME}[0].default.database[0].characterSet" "UTF8"

parseConfig "CONFIG_DB_STARTSVC" ".${PBASE_CONFIG_NAME}[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".${PBASE_CONFIG_NAME}[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".${PBASE_CONFIG_NAME}[0].default.database[0].name" "mastodon_production"
parseConfig "CONFIG_DB_USER"     ".${PBASE_CONFIG_NAME}[0].default.database[0].user" "mastodon"
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

## make sure certbot is installed
HAS_CERTBOT_INSTALLED="$(which certbot)"

if [[ -z "${HAS_CERTBOT_INSTALLED}" ]] ; then
  echo "Certbot not installed"
  EXECUTE_CERTBOT_CMD="false"
else
  echo "Certbot is installed     ${HAS_CERTBOT_INSTALLED}"
fi

DASH_D_ADDITIONAL_SUBDOMAIN=""

if [[ $ADDITIONAL_SUBDOMAIN != "" ]] ; then
  DASH_D_ADDITIONAL_SUBDOMAIN="-d $ADDITIONAL_SUBDOMAIN.$THISDOMAINNAME"
fi


## fetch previously registered domain names
DOMAIN_NAME_LIST=""
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

if [[ -e "${SAVE_CMD_DIR}/domain-name-list.txt" ]] ; then
  read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"
fi

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

echo "Checking rbenv"
su - mastodon -c "rbenv --version"


## REDIS
echo ""
echo "Starting redis service"
systemctl daemon-reload
systemctl enable redis

systemctl start redis
systemctl status redis


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

## LETS ENCRYPT - HTTPS CERTIFICATE
echo ""

CERTBOT_CMD="certbot certonly --standalone --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"

if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
  echo "Executing:               ${CERTBOT_CMD}"
  eval "${CERTBOT_CMD}"

  echo "Enabling ssl_certificate in nginx.conf"
  sed -i -e "s/# ssl_certificate/ssl_certificate/g" /home/mastodon/live/dist/nginx.conf
else
  echo "Skipping execute:        EXECUTE_CERTBOT_CMD=false"
  echo "                         ${CERTBOT_CMD}"
fi

echo "Copy systemctl files:    /etc/systemd/system/"
cp /home/mastodon/live/dist/mastodon-*.service /etc/systemd/system/

ls -l /etc/systemd/system/mastodon-*.service

if [[ -e /etc/nginx/conf.d/mastodon.conf ]]; then
  echo "Already configured:      /etc/nginx/conf.d/mastodon.conf"
else
  echo "Setting domain name:     ${FULLDOMAINNAME}"
  sed -i -e "s/example.com/${FULLDOMAINNAME}/g" /home/mastodon/live/dist/nginx.conf

  echo "NGINX Configuration:     /etc/nginx/conf.d/mastodon.conf"
  cp /home/mastodon/live/dist/nginx.conf /etc/nginx/conf.d/mastodon.conf
fi


echo ""
echo "Starting nginx service"
systemctl daemon-reload

systemctl enable nginx
systemctl start nginx


## CONFIGURE MASTODON
## copy sample template and fill in config params

echo "Configuring:             /home/mastodon/live/.env.production"
cd /home/mastodon/live/

ENV_PRODUCTION_FILENAME=".env.production"
/bin/cp -f .env.production.sample .env.production


## Generate secrets
SECRET_KEY_BASE=$(su - mastodon -c "cd ~/live  &&  RAILS_ENV=production bundle exec rake secret")
OTP_SECRET=$(su - mastodon -c "cd ~/live  &&  RAILS_ENV=production bundle exec rake secret")

echo "SECRET_KEY_BASE:         $SECRET_KEY_BASE"
echo "OTP_SECRET:              $OTP_SECRET"

echo "Configuring Mastodon:    $ENV_PRODUCTION_FILENAME"

sed -i -e "s/^DB_HOST=.*/DB_HOST=$CONFIG_DB_HOSTNAME/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^DB_USER=.*/DB_USER=$CONFIG_DB_USER/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^DB_NAME=.*/DB_NAME=$CONFIG_DB_NAME/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^DB_PASS=.*/DB_PASS=$CONFIG_DB_PSWD/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^DB_PORT=.*/DB_PORT=$CONFIG_DB_PORT/"  $ENV_PRODUCTION_FILENAME

sed -i -e "s/^LOCAL_DOMAIN=.*/LOCAL_DOMAIN=$FULLDOMAINNAME/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^SECRET_KEY_BASE=.*/SECRET_KEY_BASE=$SECRET_KEY_BASE/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^OTP_SECRET=.*/OTP_SECRET=$OTP_SECRET/"  $ENV_PRODUCTION_FILENAME

sed -i -e "s/^SMTP_SERVER=.*/SMTP_SERVER=$SMTP_SERVER/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^SMTP_PORT=.*/SMTP_PORT=$SMTP_PORT/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^SMTP_LOGIN=.*/SMTP_LOGIN=$SMTP_LOGIN/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^SMTP_PASSWORD=.*/SMTP_PASSWORD=$SMTP_PASSWORD/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^SMTP_SERVER=.*/SMTP_SERVER=$SMTP_SERVER/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^SMTP_FROM_ADDRESS=.*/SMTP_FROM_ADDRESS=notifications@${THISDOMAINNAME}/"  $ENV_PRODUCTION_FILENAME

#echo "Setting SECRET_KEY_BASE in config/secrets.yml"
#sed -i "s/<%= ENV\[\"SECRET_KEY_BASE\"\] %>/$SECRET_KEY_BASE/"  /home/mastodon/live/config/secrets.yml

## generate vapid keys
VAPID_PAIR=$(su - mastodon -c "cd ~/live  &&  RAILS_ENV=production bundle exec rake mastodon:webpush:generate_vapid_key")

echo "Vapid key pair generated"
##echo $VAPID_PAIR

VAPIDPRIVATEKEY=$(echo $VAPID_PAIR | cut -f 1 -d' ')
VAPIDPUBLICKEY=$(echo $VAPID_PAIR | cut -f 2 -d' ')

VPRIVATEKEY=$(echo $VAPIDPRIVATEKEY | sed s/VAPID_PRIVATE_KEY=//)
VPUBLICKEY=$(echo $VAPIDPUBLICKEY | sed s/VAPID_PUBLIC_KEY=//)

echo "VAPID_PRIVATE_KEY:       $VPRIVATEKEY"
echo "VAPID_PUBLIC_KEY:        $VPUBLICKEY"

## set vapid keys
sed -i -e "s/^VAPID_PRIVATE_KEY=.*/VAPID_PRIVATE_KEY=$VPRIVATEKEY/"  $ENV_PRODUCTION_FILENAME
sed -i -e "s/^VAPID_PUBLIC_KEY=.*/VAPID_PUBLIC_KEY=$VPUBLICKEY/"  $ENV_PRODUCTION_FILENAME


echo ""  >>  $ENV_PRODUCTION_FILENAME
echo "# Added by RPM"  >>  $ENV_PRODUCTION_FILENAME
echo "# ------------"  >>  $ENV_PRODUCTION_FILENAME

## may have separate WEB_DOMAIN
if [[ $WEB_DOMAIN_NAME != "" ]] ; then
  echo "WEB_DOMAIN:              $WEB_DOMAIN_NAME"
  echo "WEB_DOMAIN=${WEB_DOMAIN_NAME}"  >>  $ENV_PRODUCTION_FILENAME
fi


## may have enable secure mode
if [[ $AUTHORIZED_FETCH == "true" ]] ; then
  echo "AUTHORIZED_FETCH:        $AUTHORIZED_FETCH"
  echo "AUTHORIZED_FETCH=true"  >>  $ENV_PRODUCTION_FILENAME
fi

if [[ $LIMITED_FEDERATION_MODE == "true" ]] ; then
  echo "LIMITED_FEDERATION_MODE: $LIMITED_FEDERATION_MODE"
  echo "LIMITED_FEDERATION_MODE=true"  >>  $ENV_PRODUCTION_FILENAME
fi



## TODO: configure with values in pbase_s3storage.json
## S3 STORAGE CONFIG
sed -i -e "s/^S3_ENABLED=.*/S3_ENABLED=false/g"  $ENV_PRODUCTION_FILENAME


## add lines for SMTP_AUTH and SAFETY_ASSURED flag
echo ""  >>  $ENV_PRODUCTION_FILENAME
echo "SMTP_AUTH_METHOD=${SMTP_AUTH_METHOD}"  >>  $ENV_PRODUCTION_FILENAME
echo "SMTP_OPENSSL_VERIFY_MODE=${SMTP_OPENSSL_VERIFY_MODE}"  >>  $ENV_PRODUCTION_FILENAME
echo ""  >>  $ENV_PRODUCTION_FILENAME


## SINGLE_USER_MODE
if [[ $SINGLE_USER_MODE == "true" ]]; then
  echo "Configuring:             SINGLE_USER_MODE=true"
  echo "SINGLE_USER_MODE=true"  >>  $ENV_PRODUCTION_FILENAME
fi

## set SAFETY_ASSURED flag in env file to enable DB setup
echo "SAFETY_ASSURED=1"  >>  $ENV_PRODUCTION_FILENAME

chown mastodon:mastodon /home/mastodon/live/$ENV_PRODUCTION_FILENAME

## CRON
echo "Adding cron jobs:        /etc/crontab"

## create empty log files
CRONJOB_LOGFILE="/var/log/letsencrypt-sslrenew.log"
TOOLCTL_LOGFILE="/var/log/mastodon-toolctl-media-remove.log"

## run tasks at random minute - under 0:50, random hour before 11pm

RAND_MINUTE="$((2 + RANDOM % 50))"
RAND_HOUR="$((2 + RANDOM % 23))"
CRONJOB_LINE1="${RAND_MINUTE} ${RAND_HOUR} * * * root /usr/bin/certbot renew --deploy-hook '/bin/systemctl reload nginx' >> $CRONJOB_LOGFILE"

RAND_MINUTE="$((2 + RANDOM % 50))"
RAND_HOUR="$((2 + RANDOM % 23))"
CRONJOB_LINE2="${RAND_MINUTE} ${RAND_HOUR} * * 4 mastodon cd /home/mastodon/live && RAILS_ENV=production /home/mastodon/.rbenv/shims/bundle exec /home/mastodon/live/bin/tootctl media remove --days=30 >> ${TOOLCTL_LOGFILE} 2>&1"

echo ""  >>  /etc/crontab
echo "## Added by activpb-mastodon RPM ##"  >>  /etc/crontab

if [[ $CONFIG_ENABLE_AUTORENEW == "true" ]]; then
  touch "$CRONJOB_LOGFILE"
  chown root:root ${CRONJOB_LOGFILE}
  echo "$CRONJOB_LINE1"  >>  /etc/crontab
fi

touch "$TOOLCTL_LOGFILE"
chown mastodon:mastodon ${TOOLCTL_LOGFILE}

echo "$CRONJOB_LINE2"  >>  /etc/crontab

## finish setup
echo "Executing:               bundle exec rails db:setup"
su - mastodon -c "cd ~/live  &&  RAILS_ENV=production bundle exec rails db:setup"

echo "Executing:               bundle exec rails assets:precompile"
su - mastodon -c "cd ~/live  &&  RAILS_ENV=production bundle exec rails assets:precompile"

## unset SAFETY_ASSURED flag - DB setup is done
sed -i -e "s/SAFETY_ASSURED=1//"  $ENV_PRODUCTION_FILENAME


## Add aliases helpful for admin tasks to .bashrc
echo "" >> /root/.bashrc
append_bashrc_alias tailnginx "tail -f /var/log/nginx/error.log /var/log/nginx/access.log"
append_bashrc_alias tailmastodon "journalctl -xf -u mastodon-*"

append_bashrc_alias statusmastodon "systemctl status mastodon-*"
append_bashrc_alias stopmastodon "systemctl stop mastodon-*"
append_bashrc_alias startmastodon "systemctl start mastodon-*"
append_bashrc_alias restartmastodon "systemctl restart mastodon-*"

append_bashrc_alias editmastodonconf "vi /home/mastodon/live/.env.production"
append_bashrc_alias editnginxconf "vi /etc/nginx/conf.d/mastodon.conf"

append_bashrc_alias statusnginx "systemctl status nginx"
append_bashrc_alias stopnginx "systemctl stop nginx"
append_bashrc_alias startnginx "systemctl start nginx"
append_bashrc_alias restartnginx "systemctl restart nginx"


echo ""
echo "Starting mastodon services"

systemctl enable mastodon-web mastodon-sidekiq mastodon-streaming
systemctl start mastodon-web mastodon-sidekiq mastodon-streaming

systemctl status mastodon-web

echo "Mastodon configuration:  /home/mastodon/live/.env.production"

EXTERNALURL="https://${FULLDOMAINNAME}"
echo ""
echo "Next Step - required - open your Mastodon instance now at the URL below"
echo "                       and click 'Create Account' to create your administrator account"
echo ""

echo "Mastodon Ready:            $EXTERNALURL"
echo ""

%files
