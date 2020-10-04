Name: activpb-pleroma
Version: 1.0
Release: 0
Summary: PBase Pleroma dependencies and service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: activpb-pleroma
Requires: erlang, erlang-parsetools, erlang-xmerl, elixir, nginx, openssl, certbot

%description
PBase Pleroma service

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
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/activpb_pleroma.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "activpb_pleroma.json"
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


echo "PBase Pleroma server"

## Pleroma config
## look for either separate config file "activpb_pleroma.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="activpb_pleroma.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "HTTP_PORT" ".activpb_pleroma.httpPort" "8065"
parseConfig "ADD_APACHE_PROXY" ".activpb_pleroma.addApacheProxy" "false"
parseConfig "USE_SUB_DOMAIN" ".activpb_pleroma.useSubDomain" "false"
parseConfig "SUB_DOMAIN_NAME" ".activpb_pleroma.subDomainName" ""

echo "HTTP_PORT:               $HTTP_PORT"
echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"
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

parseConfig "CONFIG_DB_NAME"     ".${PBASE_CONFIG_NAME}[0].default.database[0].name" "pleroma_prod"
parseConfig "CONFIG_DB_USER"     ".${PBASE_CONFIG_NAME}[0].default.database[0].user" "pleroma"
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


## POSTGRES
echo "Enable Postgres extensions used by PeerTube"
echo "                         psql -c 'CREATE EXTENSION pg_trgm;' $CONFIG_DB_NAME"
echo "                         psql -c 'CREATE EXTENSION unaccent;' $CONFIG_DB_NAME"

su - postgres -c "psql -c 'CREATE EXTENSION pg_trgm;' $CONFIG_DB_NAME"
su - postgres -c "psql -c 'CREATE EXTENSION unaccent;' $CONFIG_DB_NAME"


## USER
echo "Creating group and user: pleroma"
mkdir -p /var/www/

adduser \
   --system \
   --shell /bin/bash \
   --comment 'Pleroma service' \
   --user-group \
   --home /var/lib/pleroma -m \
   pleroma

chmod +x /var/lib/pleroma

## make sub-directories
mkdir -p /opt/pleroma

cd /opt/pleroma
git clone -b stable https://git.pleroma.social/pleroma/pleroma /opt/pleroma
chown -R pleroma:pleroma /opt/pleroma


echo "Executing:               mix local.hex --force"
su - pleroma -c "cd /opt/pleroma/ && mix local.hex --force"

echo "Executing:               mix local.rebar --force"
su - pleroma -c "cd /opt/pleroma/ && mix local.rebar --force"

echo "Executing:               mix deps.get"
su - pleroma -c "cd /opt/pleroma/ && mix deps.get"



## -------------

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

sed -i "s/example.com/$THISDOMAINNAME/g" /var/www/pleroma/config/production.yaml

QT="'"
CONFIG_DB_USERQT=${QT}${CONFIG_DB_USER}${QT}
CONFIG_DB_PSWDQT=${QT}${CONFIG_DB_PSWD}${QT}

sed -i "s/username: 'pleroma'/username: $CONFIG_DB_USERQT/" /var/www/pleroma/config/production.yaml
sed -i "s/password: 'pleroma'/password: $CONFIG_DB_PSWDQT/" /var/www/pleroma/config/production.yaml


echo "Nginx config:            /etc/nginx/conf.d/pleroma.conf"
/bin/cp -f --no-clobber /var/www/pleroma/pleroma-latest/support/nginx/pleroma /etc/nginx/conf.d/pleroma.conf

sed -i "s/pleroma.example.com/$THISDOMAINNAME/g" /etc/nginx/conf.d/pleroma.conf

## LETS ENCRYPT - HTTPS CERTIFICATE

if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
  echo "Executing:               certbot certonly --standalone -d ${THISDOMAINNAME} -m ${EMAIL_ADDR} --agree-tos -n"
  certbot certonly --standalone -d ${THISDOMAINNAME} -m ${EMAIL_ADDR} --agree-tos -n
fi

echo "Configuration updated:   /etc/nginx/conf.d/pleroma.conf"

echo "TCP/IP Tuning:           /etc/sysctl.d/30-pleroma-tcp.conf"
cp /var/www/pleroma/pleroma-latest/support/sysctl.d/30-pleroma-tcp.conf /etc/sysctl.d/
sysctl -p /etc/sysctl.d/30-pleroma-tcp.conf


echo "Starting NGINX service"
systemctl daemon-reload

systemctl enable nginx
systemctl start nginx
systemctl status pleroma

echo "Starting pleroma.service"
/bin/cp -f --no-clobber /var/www/pleroma/pleroma-latest/support/systemd/pleroma.service /etc/systemd/system/

systemctl enable pleroma
systemctl start pleroma
systemctl status pleroma


## Add aliases helpful for admin tasks to .bashrc
#echo "" >> /root/.bashrc
#append_bashrc_alias tailnginx "tail -f /var/log/nginx/error.log /var/log/nginx/access.log"

echo "Pleroma installed"
echo "Show logs with:          journalctl -feu pleroma"

%files
