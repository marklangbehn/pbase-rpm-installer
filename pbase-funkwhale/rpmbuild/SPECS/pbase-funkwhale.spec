Name: pbase-funkwhale
Version: 1.0
Release: 0
Summary: PBase Funkwhale service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-funkwhale-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-funkwhale
Requires: nginx, postgresql, openssl, openssl-devel, openldap-devel, libjpeg-devel, libpq-devel, python3-devel, wget, redis, git, make, gcc, ffmpeg, nodejs, unzip, certbot, jq, python3-pip, python3-virtualenv, libffi-devel, bzip2-devel, gettext, file-libs, lame

%description
PBase Funkwhale service

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

## config is stored in json file with root-only permsissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_funkwhale.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_funkwhale.json"
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

echo "PBase Funkwhale server install"

## check if already installed
if [[ -e "/srv/funkwhale/config/.env" ]]; then
  echo "/srv/funkwhale/config/.env already exists - exiting"
  exit 0
fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## funkwhale config
## look for either separate config file "pbase_funkwhale.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_funkwhale.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "FUNKWHALE_VERSION" ".pbase_funkwhale.funkwhaleVersion" "1.0"
parseConfig "HTTP_PORT" ".pbase_funkwhale.port" "4000"
parseConfig "ADD_NGINX_PROXY" ".pbase_funkwhale.addNgnixProxy" "false"
parseConfig "USE_SUB_DOMAIN" ".pbase_funkwhale.useSubDomain" "false"
parseConfig "SUB_DOMAIN_NAME" ".pbase_funkwhale.subDomainName" ""

echo "HTTP_PORT:               $HTTP_PORT"
echo "ADD_NGINX_PROXY:         $ADD_NGINX_PROXY"
echo "USE_SUB_DOMAIN:          $USE_SUB_DOMAIN"
echo "SUB_DOMAIN_NAME:         $SUB_DOMAIN_NAME"


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
parseConfig "CONFIG_DB_CHARSET"  ".${PBASE_CONFIG_NAME}[0].default.characterSet" "UTF8"

parseConfig "CONFIG_DB_STARTSVC" ".${PBASE_CONFIG_NAME}[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".${PBASE_CONFIG_NAME}[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".${PBASE_CONFIG_NAME}[0].default.database[0].name" "funkwhale_prod"
parseConfig "CONFIG_DB_USER"     ".${PBASE_CONFIG_NAME}[0].default.database[0].user" "funkwhale"
parseConfig "CONFIG_DB_PSWD"     ".${PBASE_CONFIG_NAME}[0].default.database[0].password" $RAND_PW_USER

echo "CONFIG_DB_HOSTNAME:      $CONFIG_DB_HOSTNAME"
echo "CONFIG_DB_PORT:          $CONFIG_DB_PORT"
echo "CONFIG_DB_CHARSET:       $CONFIG_DB_CHARSET"

echo "CONFIG_DB_STARTSVC:      $CONFIG_DB_STARTSVC"
echo "CONFIG_DB_INSTALL:       $CONFIG_DB_INSTALL"
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
echo "PBASE_CONFIG_NAME:       $PBASE_CONFIG_NAME"

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



## S3 STORAGE CONFIG
echo ""
PBASE_CONFIG_FILENAME="pbase_s3storage.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "S3_ENABLED" ".pbase_s3storage.s3Enabled" "false"
parseConfig "AWS_STORAGE_BUCKET_NAME" ".pbase_s3storage.s3Bucket" "true"
parseConfig "AWS_ACCESS_KEY_ID" ".pbase_s3storage.awsAccessKeyId" ""
parseConfig "AWS_SECRET_ACCESS_KEY" ".pbase_s3storage.awsSecretAccessKeyId" ""

parseConfig "AWS_S3_REGION_NAME" ".pbase_s3storage.awsS3RegionName" ""
parseConfig "AWS_S3_CUSTOM_DOMAIN" ".pbase_s3storage.awsS3CustomDomain" ""
parseConfig "AWS_S3_ENDPOINT_URL" ".pbase_s3storage.awsS3EndpointUrl" ""
parseConfig "PROXY_MEDIA" ".pbase_s3storage.proxyMedia" ""


echo "Config S3_ENABLED:       $S3_ENABLED"

if [[ $S3_ENABLED == "true" ]]; then
  echo "AWS_STORAGE_BUCKET_NAME: $AWS_STORAGE_BUCKET_NAME"
  echo "AWS_ACCESS_KEY_ID:       $AWS_ACCESS_KEY_ID"
  echo "AWS_SECRET_ACCESS_KEY:   $AWS_SECRET_ACCESS_KEY"
  echo "AWS_S3_REGION_NAME:      $AWS_S3_REGION_NAME"
  echo "AWS_S3_CUSTOM_DOMAIN:    $AWS_S3_CUSTOM_DOMAIN"
  echo "AWS_S3_ENDPOINT_URL:     $AWS_S3_ENDPOINT_URL"
  echo "PROXY_MEDIA:             $PROXY_MEDIA"
fi


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
echo "Enable Postgres extensions used by Funkwhale"
echo "                         psql -c 'CREATE EXTENSION citext;' $CONFIG_DB_NAME"
echo "                         psql -c 'CREATE EXTENSION unaccent;' $CONFIG_DB_NAME"

su - postgres -c "psql -c 'CREATE EXTENSION citext;' $CONFIG_DB_NAME"
su - postgres -c "psql -c 'CREATE EXTENSION unaccent;' $CONFIG_DB_NAME"


## USER
echo "Creating group and user: funkwhale"
mkdir -p /srv/funkwhale

adduser \
   --system \
   --shell /bin/bash \
   --comment 'Funkwhale service' \
   --user-group \
   --home /srv/funkwhale -m \
   funkwhale


## DOWNLOAD CODE
cd /srv/funkwhale

echo "Adding directories"
mkdir -p api config data/static data/media data/music


echo "Downloading api release"
curl -s -L -o "api.zip" "https://dev.funkwhale.audio/funkwhale/funkwhale/-/jobs/artifacts/$FUNKWHALE_VERSION/download?job=build_api"
unzip -q "api.zip" -d extracted
mv extracted/api/* api/
/bin/rm -rf extracted
/bin/rm -f api.zip

echo "Downloading frontend files"
curl -s -L -o "front.zip" "https://dev.funkwhale.audio/funkwhale/funkwhale/-/jobs/artifacts/$FUNKWHALE_VERSION/download?job=build_front"
unzip -q "front.zip" -d extracted
mv extracted/front .
/bin/rm -rf extracted
/bin/rm -f front.zip

## set ownership
chown -R funkwhale:funkwhale /srv/funkwhale/


## PYTHON VIRUALENV
echo "Executing:               python3 -m venv /srv/funkwhale/virtualenv"
cd /srv/funkwhale
python3 -m venv /srv/funkwhale/virtualenv


echo "Executing:               source /srv/funkwhale/virtualenv/bin/activate"
source /srv/funkwhale/virtualenv/bin/activate

echo "Installing Python dependencies"
pip3 install wheel
pip3 install -r api/requirements/base.txt
pip3 install -r api/requirements/local.txt
pip3 install -r api/requirements/test.txt


echo "Downloading sample environment file"
curl -s -L -o config/.env "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/master/deploy/env.prod.sample"

echo "Configuring:             /srv/funkwhale/config/.env"
chmod +rw /srv/funkwhale/config/.env

DJANGO_SECRET_KEY="$(openssl rand -base64 45)"
echo "DJANGO_SECRET_KEY:       $DJANGO_SECRET_KEY"

## modify in-place
## sed -i "s/^DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY/"  /srv/funkwhale/config/.env

sed -i "s/^DJANGO_SECRET_KEY/#DJANGO_SECRET_KEY/"  /srv/funkwhale/config/.env
sed -i "s/^FUNKWHALE_HOSTNAME=.*/FUNKWHALE_HOSTNAME=$THISDOMAINNAME/"  /srv/funkwhale/config/.env


DJANGO_KEY_LINE="DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}"
DATABASE_URL_LINE="DATABASE_URL=postgresql://funkwhale@:5432/funkwhale"
CACHE_URL_LINE="CACHE_URL=redis://localhost:6379/0"
CELERY_CO_LINE="CELERYD_CONCURRENCY=0"

## add to bottom of file
echo ""  >>  /srv/funkwhale/config/.env
echo "$DJANGO_KEY_LINE"  >>  /srv/funkwhale/config/.env
echo "$DATABASE_URL_LINE"  >>  /srv/funkwhale/config/.env
echo "$CACHE_URL_LINE"  >>  /srv/funkwhale/config/.env
echo "$CELERY_CO_LINE"  >>  /srv/funkwhale/config/.env


## SMTP config-line sample:
##   EMAIL_CONFIG=smtp+tls://user:password@youremail.host:587
##   EMAIL_CONFIG=smtp+tls://postmaster%40mail.pbase-foundation.social:a12345678b234567c9876543-987654d@smtp.mailgun.org:587

## must url encode the embedded @ character
SMTP_LOGIN_URLENCODED=${SMTP_LOGIN/@/%40}


EMAIL_CONFIG_LINE="EMAIL_CONFIG=smtp+tls://${SMTP_LOGIN_URLENCODED}:${SMTP_PASSWORD}@${SMTP_SERVER}:${SMTP_PORT}"
VERI_ENFORCE_LINE="ACCOUNT_EMAIL_VERIFICATION_ENFORCE=true"
DEFAULT_FROM_LINE="DEFAULT_FROM_EMAIL=noreply@${THISDOMAINNAME}"

echo "SMTP config:             $EMAIL_CONFIG_LINE"

echo "" >>  /srv/funkwhale/config/.env
echo "$EMAIL_CONFIG_LINE"  >>  /srv/funkwhale/config/.env
echo "$VERI_ENFORCE_LINE"  >>  /srv/funkwhale/config/.env
echo "$DEFAULT_FROM_LINE"  >>  /srv/funkwhale/config/.env
echo "" >>  /srv/funkwhale/config/.env


## S3 CONFIG

if [[ $S3_ENABLED == "true" ]]; then
  if [[ $AWS_STORAGE_BUCKET_NAME != "" ]]; then
    sed -i "s/^AWS_STORAGE_BUCKET_NAME/#AWS_STORAGE_BUCKET_NAME/"  /srv/funkwhale/config/.env
    echo "AWS_STORAGE_BUCKET_NAME=$AWS_STORAGE_BUCKET_NAME"  >>  /srv/funkwhale/config/.env
  fi

  if [[ $AWS_ACCESS_KEY_ID != "" ]]; then
    sed -i "s/^AWS_ACCESS_KEY_ID/#AWS_ACCESS_KEY_ID/"  /srv/funkwhale/config/.env
    echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"  >>  /srv/funkwhale/config/.env
  fi

  if [[ $AWS_SECRET_ACCESS_KEY != "" ]]; then
    sed -i "s/^AWS_SECRET_ACCESS_KEY/#AWS_SECRET_ACCESS_KEY/"  /srv/funkwhale/config/.env
    echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"  >>  /srv/funkwhale/config/.env
  fi

  if [[ $AWS_S3_REGION_NAME != "" ]]; then
    sed -i "s/^AWS_S3_REGION_NAME/#AWS_S3_REGION_NAME/"  /srv/funkwhale/config/.env
    echo "AWS_S3_REGION_NAME=$AWS_S3_REGION_NAME"  >>  /srv/funkwhale/config/.env
  fi

  if [[ $AWS_S3_CUSTOM_DOMAIN != "" ]]; then
    sed -i "s/^AWS_S3_CUSTOM_DOMAIN/#AWS_S3_CUSTOM_DOMAIN/"  /srv/funkwhale/config/.env
    echo "AWS_S3_CUSTOM_DOMAIN=$AWS_S3_CUSTOM_DOMAIN"  >>  /srv/funkwhale/config/.env
  fi

  if [[ $AWS_S3_ENDPOINT_URL != "" ]]; then
    sed -i "s/^AWS_S3_ENDPOINT_URL/#AWS_S3_ENDPOINT_URL/"  /srv/funkwhale/config/.env
    echo "AWS_S3_ENDPOINT_URL=$AWS_S3_ENDPOINT_URL"  >>  /srv/funkwhale/config/.env
  fi

  if [[ $PROXY_MEDIA != "" ]]; then
    sed -i "s/^PROXY_MEDIA/#PROXY_MEDIA/"  /srv/funkwhale/config/.env
    echo "PROXY_MEDIA=$PROXY_MEDIA"  >>  /srv/funkwhale/config/.env
  fi

  echo "" >>  /srv/funkwhale/config/.env
fi

## BUILD

echo ""
echo "Executing DB create:     python api/manage.py migrate"
su - funkwhale -c "source /srv/funkwhale/virtualenv/bin/activate  &&  cd /srv/funkwhale  &&  python3 api/manage.py migrate"

#echo ""
#echo "Initial user account:    python3 api/manage.py createsuperuser"
#su - funkwhale -c "source /srv/funkwhale/virtualenv/bin/activate  &&  cd /srv/funkwhale  &&  python3 api/manage.py createsuperuser"

echo ""
echo "Static resources:        python api/manage.py collectstatic"
su - funkwhale -c "source /srv/funkwhale/virtualenv/bin/activate  &&  cd /srv/funkwhale  &&  python3 api/manage.py collectstatic"


# create a final nginx configuration using the template based on your environment
cd /usr/local/pbase-data/pbase-funkwhale/etc-nginx-conf-d

set -a && source /srv/funkwhale/config/.env && set +a
envsubst "`env | awk -F = '{printf \" $%s\", $$1}'`"  <  nginx.template  >  funkwhale.conf

ls -l

/bin/cp -f --no-clobber funkwhale.conf /etc/nginx/conf.d/
/bin/cp -f --no-clobber funkwhale_proxy.conf /etc/nginx/

echo "Nginx configuration:     /etc/nginx/conf.d/"
ls -l /etc/nginx/conf.d/


## LETS ENCRYPT - HTTPS CERTIFICATE
echo ""

if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
  echo "Executing:               certbot certonly --standalone -d ${THISDOMAINNAME} -m ${EMAIL_ADDR} --agree-tos -n"
  certbot certonly --standalone -d ${THISDOMAINNAME} -m ${EMAIL_ADDR} --agree-tos -n
else
  echo "Skipping certbot:      EXECUTE_CERTBOT_CMD=false"
fi


## Add aliases helpful for admin tasks to .bashrc
## add aliases
echo ""
echo "" >> /root/.bashrc
append_bashrc_alias tailnginx "tail -f /var/log/nginx/error.log /var/log/nginx/access.log"
append_bashrc_alias tailfunkwhale "journalctl -xf -u funkwhale-*"

append_bashrc_alias statusfunkwhale "systemctl status funkwhale-*"
append_bashrc_alias stopfunkwhale "systemctl stop funkwhale-*"
append_bashrc_alias startfunkwhale "systemctl start funkwhale-*"
append_bashrc_alias restartfunkwhale "systemctl restart funkwhale-*"

append_bashrc_alias editnginxconf "vi /etc/nginx/conf.d/funkwhale.conf"
append_bashrc_alias editfunkwhaleconf "vi /srv/funkwhale/config/.env"


echo ""
echo "Starting nginx service"
systemctl daemon-reload

systemctl enable nginx
systemctl start nginx
systemctl status nginx


## restrict permissions
chmod 0600 /srv/funkwhale/config/.env
chown funkwhale:funkwhale /srv/funkwhale/config/.env

echo "Funkwhale services:      /etc/systemd/system/"
/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-funkwhale/etc-systemd-system/*  /etc/systemd/system/

systemctl daemon-reload

systemctl enable funkwhale-server.service funkwhale-worker.service funkwhale-beat.service
systemctl start funkwhale-server.service funkwhale-worker.service funkwhale-beat.service
systemctl status funkwhale-server


echo ""
echo "Next Step - required - you must create your admin account first with"
echo "                         the command-line now as 'root' user with either: "
echo "  su - funkwhale -c \"source /srv/funkwhale/virtualenv/bin/activate  &&  python api/manage.py createsuperuser\""

echo ""
echo "                         ... or with separate commands as 'funkwhale' user:"
echo "  su - funkwhale"
echo "  source /srv/funkwhale/virtualenv/bin/activate"
echo "  python api/manage.py createsuperuser"
echo "                         ... then enter you admin user name and password."
echo ""

EXTERNALURL="https://$THISDOMAINNAME"
echo "Funkwhale Ready:          $EXTERNALURL"
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-funkwhale/etc-nginx-conf-d/funkwhale_proxy.conf
/usr/local/pbase-data/pbase-funkwhale/etc-nginx-conf-d/nginx.template
/usr/local/pbase-data/pbase-funkwhale/etc-systemd-system/funkwhale.target
/usr/local/pbase-data/pbase-funkwhale/etc-systemd-system/funkwhale-beat.service
/usr/local/pbase-data/pbase-funkwhale/etc-systemd-system/funkwhale-server.service
/usr/local/pbase-data/pbase-funkwhale/etc-systemd-system/funkwhale-worker.service

