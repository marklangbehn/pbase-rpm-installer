Name: pbase-gotty
Version: 1.0
Release: 0
Summary: PBase GoTTY rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-gotty-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-gotty
Requires: pbase-lets-encrypt-transitive-dep, git, jq

%description
PBase GoTTY service

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

echo "PBase GoTTY install"

## check if already installed
if [[ -e "/usr/local/bin/gotty" ]]; then
  echo "/usr/local/bin/gotty already exists - exiting"
  exit 0
fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## GoTTY config
## look for config file "pbase_gotty.json"
PBASE_CONFIG_FILENAME="pbase_gotty.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "ENABLE_AUTORENEW" ".pbase_gotty.enableAutoRenew" "true"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_gotty.executeCertbotCmd" "true"

parseConfig "URL_SUB_DOMAIN" ".pbase_gotty.urlSubDomain" "shell"
parseConfig "EMAIL_ADDRESS" ".pbase_gotty.emailAddress" "yoursysadmin@yourrealmail.com"
parseConfig "AUTH_USERNAME" ".pbase_gotty.basicAuthUsername" "mark"
parseConfig "AUTH_PASSWORD" ".pbase_gotty.basicAuthPassword" "shomeddata"

echo "ENABLE_AUTORENEW:        $ENABLE_AUTORENEW"
echo "EXECUTE_CERTBOT_CMD:     $EXECUTE_CERTBOT_CMD"

echo "URL_SUB_DOMAIN:          $URL_SUB_DOMAIN"
echo "EMAIL_ADDRESS:           $EMAIL_ADDRESS"
echo "AUTH_USERNAME:           $AUTH_USERNAME"
echo "AUTH_PASSWORD:           $AUTH_PASSWORD"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

if [[ "$URL_SUB_DOMAIN" != "" ]] ; then
  FULLDOMAINNAME="${URL_SUB_DOMAIN}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi


cd /root

echo ""
echo "Building code:           go get -v github.com/yudai/gotty"

go get -v github.com/yudai/gotty

/bin/cp --no-clobber /root/go/bin/gotty /usr/local/bin
chmod +x /usr/local/bin/gotty

echo "GoTTY binary compiled:"
ls -lh /usr/local/bin/gotty
echo ""

echo "Launch script:"
echo "  /usr/local/pbase-data/pbase-gotty/script/launch-gotty.sh"
echo ""

## add gotty service file
/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-gotty/etc-systemd-system/gotty.service /etc/systemd/system/


if [[ "${AUTH_USERNAME}" != "" ]] && [[ "${AUTH_PASSWORD}" != "" ]] ; then
  HTTP_AUTH_CREDENTIAL="${AUTH_USERNAME}:${AUTH_PASSWORD}"
  echo "Setting HTTP auth:       ${HTTP_AUTH_CREDENTIAL}"

  sed -i -e "s/mark:shomeddata/${HTTP_AUTH_CREDENTIAL}/" /etc/systemd/system/gotty.service
  sed -i -e "s/mark:shomeddata/${HTTP_AUTH_CREDENTIAL}/" /usr/local/pbase-data/pbase-gotty/script/launch-gotty.sh
else
  echo "HTTP auth must be set:   /etc/systemd/system/gotty.service"
fi

## LETS ENCRYPT - HTTPS CERTIFICATE

if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
  echo "Executing:               certbot certonly --standalone -d ${FULLDOMAINNAME} -m ${EMAIL_ADDRESS} --agree-tos -n"
  certbot certonly --standalone -d ${FULLDOMAINNAME} -m ${EMAIL_ADDRESS} --agree-tos -n
else
  echo "Not executing:           certbot certonly --standalone -d ${FULLDOMAINNAME} -m ${EMAIL_ADDRESS} --agree-tos -n"
  echo "Skipping certbot:        EXECUTE_CERTBOT_CMD=false"
fi

echo "Creating HTTPS certificate symlinks"
cd /root

ln -s /etc/letsencrypt/live/${FULLDOMAINNAME}/privkey.pem /root/.gotty.key
ln -s /etc/letsencrypt/live/${FULLDOMAINNAME}/fullchain.pem /root/.gotty.ca.crt
ln -s /etc/letsencrypt/live/${FULLDOMAINNAME}/cert.pem /root/.gotty.crt

ls -la .gotty*

echo ""

## add shell aliases
append_bashrc_alias journalgotty "journalctl -u gotty -f"
append_bashrc_alias editgottyservice "vi /etc/systemd/system/gotty.service"

append_bashrc_alias stopgotty "/bin/systemctl stop gotty"
append_bashrc_alias startgotty "/bin/systemctl start gotty"
append_bashrc_alias statusgotty "/bin/systemctl status gotty"
append_bashrc_alias restartgotty "/bin/systemctl restart gotty"


echo "Starting gotty service:  /etc/systemd/system/gotty.service"
/bin/systemctl daemon-reload

/bin/systemctl enable gotty
/bin/systemctl start gotty
/bin/systemctl status gotty


EXTERNALURL="https://$FULLDOMAINNAME"
echo "GoTTY installed:         $EXTERNALURL"
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-gotty/script/launch-gotty.sh
/usr/local/pbase-data/pbase-gotty/etc-systemd-system/gotty.service