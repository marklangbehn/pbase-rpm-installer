Name: pbase-gotty
Version: 1.0
Release: 5
Summary: PBase GoTTY rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-gotty-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-gotty
Requires: pbase-lets-encrypt-transitive-dep, git, jq, certbot, certbot-apache

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
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_gotty.json"
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

commentOutFile() {
  ## disable config file in directory $1 named $2
  echo "Checking for:            ${1}/${2}"

  if [[ -e "${1}/${2}" ]] ; then
    DATE_SUFFIX="$(date +'%Y-%m-%d_%H-%M')"

    ##echo "Backup:                  ${1}/${2}-PREV-${DATE_SUFFIX}"
    cp -p "${1}/${2}" "${1}/${2}-PREV-${DATE_SUFFIX}"

    ## comment out with a '#' in front of all lines
    echo "Commenting out contents: ${2}"
    sed -i 's/^\([^#].*\)/# \1/g' "${1}/${2}"
  fi
}

echo "PBase GoTTY install"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

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
parseConfig "ADD_APACHE_PROXY" ".pbase_gotty.addApacheProxy" "false"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_gotty.executeCertbotCmd" "true"

parseConfig "URL_SUBDOMAIN" ".pbase_gotty.urlSubDomain" "shell"
parseConfig "EMAIL_ADDR" ".pbase_gotty.emailAddress" "yoursysadmin@yourrealmail.com"
parseConfig "AUTH_USERNAME" ".pbase_gotty.basicAuthUsername" "mark"
parseConfig "AUTH_PASSWORD" ".pbase_gotty.basicAuthPassword" "shomeddata"

echo "ENABLE_AUTORENEW:        $ENABLE_AUTORENEW"
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

## Check for /etc/httpd/conf.d/ssl.conf, comment it out if it exists
commentOutFile "/etc/httpd/conf.d" "ssl.conf"


## fetch previously registered domain names
HAS_WWW_SUBDOMAIN="false"
DOMAIN_NAME_LIST=""
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

if [[ -e "${SAVE_CMD_DIR}/domain-name-list.txt" ]]; then
  read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"

  echo "Existing domain names:   ${SAVE_CMD_DIR}/domain-name-list.txt"
  echo "Found domain-name-list:  ${DOMAIN_NAME_LIST}"
else
  echo "Adding first domain:     ${SAVE_CMD_DIR}/domain-name-list.txt"
fi

echo "URL_SUBDOMAIN:           $URL_SUBDOMAIN"
echo "AUTH_USERNAME:           $AUTH_USERNAME"
echo "AUTH_PASSWORD:           $AUTH_PASSWORD"

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

echo "Found DOMAIN_NAME_LIST:  ${DOMAIN_NAME_LIST}"

if [[ "${DOMAIN_NAME_LIST}" == "" ]] ; then
  echo "Starting from empty domain-name-list.txt, adding ${FULLDOMAINNAME}"
  DOMAIN_NAME_LIST_NEW="${FULLDOMAINNAME}"
  DOMAIN_NAME_PARAM="${FULLDOMAINNAME}"
else
    ## use cut to grab first name from comma delimited list
    FIRSTDOMAINNREGISTERED=$(cut -f1 -d "," ${SAVE_CMD_DIR}/domain-name-list.txt)
    ##echo "FIRSTDOMAINNREGISTERED:  ${FIRSTDOMAINNREGISTERED}"

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

#echo "FULLDOMAINNAME:          $FULLDOMAINNAME"
#echo "SUBPATH_URI:             $SUBPATH_URI"
#echo "PROXY_CONF_FILE:         $PROXY_CONF_FILE"


cd /root

## GoTTY download from repo https://github.com/sorenisanerd/gotty
## forked from previous repo https://github.com/yudai/gotty

echo "Building code:           go install github.com/sorenisanerd/gotty@latest"

go install github.com/sorenisanerd/gotty@latest

/bin/cp --no-clobber /root/go/bin/gotty /usr/local/bin
chmod +x /usr/local/bin/gotty

echo "GoTTY binary compiled:"
ls -lh /usr/local/bin/gotty
echo ""

echo "Launch script:"
echo "  /usr/local/pbase-data/pbase-gotty/script/launch-gotty.sh"
echo ""

if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  ## add gotty service file
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-gotty/etc-systemd-system/gotty-port-18080.service /etc/systemd/system/gotty.service

  echo "Using Apache proxy"
  PREV_CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  if [[ -e "${PREV_CONF_FILE}" ]] ; then
    echo "Disabling previous:      ${PREV_CONF_FILE}"
    mv "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf-DISABLED"

    ## set aside conf file so that certbot can recreate the ...le-ssl.conf
    if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" ]] ; then
      echo "Disabling prev conf:     /etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf"
      mv "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf-DISABLED"
    fi
  fi

  /bin/cp --no-clobber /usr/local/pbase-data/pbase-gotty/etc-httpd-confd/gotty-proxy-subdomain.conf /etc/httpd/conf.d/
  mv -f "/etc/httpd/conf.d/gotty-proxy-subdomain.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

  echo "Setting subdomain:       ${CONF_FILE}"
  sed -i -e "s/shell.example.com/${FULLDOMAINNAME}/" "${CONF_FILE}"
  sed -i -e "s/example.com/${THISDOMAINNAME}/" "${CONF_FILE}"
else
  ## add gotty service file
  echo "Using direct GoTTY"
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-gotty/etc-systemd-system/gotty.service /etc/systemd/system/gotty.service
fi


if [[ "${AUTH_USERNAME}" != "" ]] && [[ "${AUTH_PASSWORD}" != "" ]] ; then
  HTTP_AUTH_CREDENTIAL="${AUTH_USERNAME}:${AUTH_PASSWORD}"
  echo "Setting HTTP auth:       ${HTTP_AUTH_CREDENTIAL}"

  sed -i -e "s/mark:shomeddata/${HTTP_AUTH_CREDENTIAL}/" /etc/systemd/system/gotty.service
  sed -i -e "s/mark:shomeddata/${HTTP_AUTH_CREDENTIAL}/" /usr/local/pbase-data/pbase-gotty/script/launch-gotty.sh
else
  echo "HTTP auth must be set:   /etc/systemd/system/gotty.service"
fi

#SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"
#echo "${FULLDOMAINNAME}" > ${SAVE_CMD_DIR}/domain-name-list.txt
#echo "Saved domain name:       ${SAVE_CMD_DIR}/domain-name-list.txt"
#echo ""


## LETS ENCRYPT - HTTPS CERTIFICATE

if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  echo "Restarting Apache"
  /bin/systemctl restart httpd

  CERTBOT_CMD="certbot --apache --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"
else
  CERTBOT_CMD="certbot certonly --standalone --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"
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
/usr/local/pbase-data/pbase-gotty/etc-systemd-system/gotty-port-18080.service
/usr/local/pbase-data/pbase-gotty/etc-httpd-confd/gotty-proxy-subdomain.conf
