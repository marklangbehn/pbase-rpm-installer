Name: pbase-webdav
Version: 1.0
Release: 2
Summary: PBase WebDAV Apache service
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-webdav-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-webdav
Requires: pbase-apache, pbase-epel, pbase-preconfig-webdav, certbot, certbot-apache

%description
PBase WebDAV service

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
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_webdav.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_webdav.json"
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


echo "PBase WebDAV installer"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

check_linux_version
echo ""
echo "Default PBase module configuration directory:"
echo "                         /usr/local/pbase-data/admin-only/module-config.d/"

## look for config file "pbase_webdav.json"
PBASE_CONFIG_FILENAME="pbase_webdav.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "WEBDAV_ALIAS" ".pbase_webdav.webDavAlias" ""
parseConfig "BASIC_AUTH_USER" ".pbase_webdav.basicAuthUsername" "webdav"
parseConfig "BASIC_AUTH_PSWD" ".pbase_webdav.basicAuthPassword" "shomeddata"

DEFAULT_EMAIL="webmaster@localhost"

## look for config file "pbase_apache.json"
PBASE_CONFIG_FILENAME="pbase_apache.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

parseConfig "ENABLE_CHECK_FOR_WWW" ".pbase_apache.enableCheckForWww" "true"
parseConfig "SERVER_ADMIN_EMAIL" ".pbase_apache.serverAdmin" "${DEFAULT_EMAIL}"
parseConfig "URL_SUBDOMAIN" ".pbase_apache.urlSubDomain" ""

echo "ENABLE_CHECK_FOR_WWW:    $ENABLE_CHECK_FOR_WWW"
echo "SERVER_ADMIN_EMAIL:      $SERVER_ADMIN_EMAIL"
echo "URL_SUBDOMAIN:           $URL_SUBDOMAIN"


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

## Checking for /etc/httpd/conf.d/ssl.conf, comment it out if it exists
commentOutFile "/etc/httpd/conf.d" "ssl.conf"

## fetch previously registered domain names
DOMAIN_NAME_LIST=""
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"

echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "Found domain-name-list:  ${DOMAIN_NAME_LIST}"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

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
    ##echo "Already has ${FULLDOMAINNAME}"
    DOMAIN_NAME_LIST_NEW="${DOMAIN_NAME_LIST}"
    DOMAIN_NAME_PARAM="${DOMAIN_NAME_LIST}"
  else
    echo "Adding ${FULLDOMAINNAME}"
    DOMAIN_NAME_LIST_NEW="${DOMAIN_NAME_LIST},${FULLDOMAINNAME}"
    DOMAIN_NAME_PARAM="${DOMAIN_NAME_LIST},${FULLDOMAINNAME} --expand"
  fi
fi

echo ""
echo "${DOMAIN_NAME_LIST_NEW}" > ${SAVE_CMD_DIR}/domain-name-list.txt
echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "                         ${DOMAIN_NAME_LIST_NEW}"
echo ""

DOMAIN_NAME_LIST_HAS_WWW=$(grep www ${SAVE_CMD_DIR}/domain-name-list.txt)
#echo "Domain list has WWW:     ${DOMAIN_NAME_LIST_HAS_WWW}"


if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" ]] ; then
  mv "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf-DISABLED"
fi

if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" ]] ; then
  mv "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf-DISABLED"
fi

echo "Configuring WebDAV"

## disable welcome page, disable displaying files within web directory
sed -i 's/^/#&/g' /etc/httpd/conf.d/welcome.conf
sed -i "s/Options Indexes FollowSymLinks/Options FollowSymLinks/" /etc/httpd/conf/httpd.conf


WEBDAV_CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
echo "Apache WebDAV config:    ${WEBDAV_CONF_FILE}"

/bin/cp --no-clobber /usr/local/pbase-data/pbase-webdav/etc-httpd-confd/webdav.conf ${WEBDAV_CONF_FILE}

echo "Admin email:             ${SERVER_ADMIN_EMAIL}"
sed -i "s/${DEFAULT_EMAIL}/${SERVER_ADMIN_EMAIL}/" "${WEBDAV_CONF_FILE}"

if [[ "${WEBDAV_ALIAS}" != "" ]]; then
  echo "webDavAlias:             ${WEBDAV_ALIAS}"
  sed -i "s|Alias /webdav|Alias /${WEBDAV_ALIAS}|" "${WEBDAV_CONF_FILE}"
fi

WEBDAV_ROOT="/var/www/html/${FULLDOMAINNAME}/${WEBDAV_ALIAS}"

sed -i "s|/var/www/html/example.com/webdav|${WEBDAV_ROOT}|g" "${WEBDAV_CONF_FILE}"
sed -i "s/example.com/${FULLDOMAINNAME}/g" "${WEBDAV_CONF_FILE}"

echo "Base directory:          ${WEBDAV_ROOT}"

mkdir -p "${WEBDAV_ROOT}"
chown -R apache:apache "${WEBDAV_ROOT}"
chmod -R 755 "${WEBDAV_ROOT}"

chown -R apache:apache /var/www/html/${FULLDOMAINNAME}
chmod -R 755 /var/www/html/${FULLDOMAINNAME}

echo "WebDev log directory:    /var/log/httpd/${FULLDOMAINNAME}"
mkdir -p "/var/log/httpd/${FULLDOMAINNAME}"

echo "Password file:           /etc/httpd/${FULLDOMAINNAME}/.htpasswd"
mkdir -p "/etc/httpd/${FULLDOMAINNAME}/"
echo "Executing command:       htpasswd -cb /etc/httpd/${FULLDOMAINNAME}/.htpasswd ${BASIC_AUTH_USER} ${BASIC_AUTH_PSWD}"

htpasswd -cb "/etc/httpd/${FULLDOMAINNAME}/.htpasswd" ${BASIC_AUTH_USER} ${BASIC_AUTH_PSWD}

chown root:apache "/etc/httpd/${FULLDOMAINNAME}/.htpasswd"
chmod 640 "/etc/httpd/${FULLDOMAINNAME}/.htpasswd"

echo "Restarting Apache"
systemctl restart httpd
systemctl status httpd

if [[ -z "${HAS_CERTBOT_INSTALLED}" ]] ; then
  echo "Certbot not installed"
else
  ## LETS ENCRYPT - HTTPS CERTIFICATE
  echo ""
  CERTBOT_CMD="certbot --apache --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"

  ## save command line in file
  echo "Saving command line:     ${SAVE_CMD_DIR}/certbot-cmd.sh"
  echo ${CERTBOT_CMD} > ${SAVE_CMD_DIR}/certbot-cmd.sh

  if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
    echo "Executing:               ${CERTBOT_CMD}"
    echo ""
    eval "${CERTBOT_CMD}"
  else
    echo "Skipping execute:        EXECUTE_CERTBOT_CMD=false"
    echo "                         ${CERTBOT_CMD}"
  fi
fi


## Add aliases helpful for admin tasks to .bashrc
echo "" >> /root/.bashrc
append_bashrc_alias tailwebdav "tail -f /var/log/httpd/${FULLDOMAINNAME}/error.log /var/log/httpd/${FULLDOMAINNAME}/access.log"
append_bashrc_alias editwebdavconf "vi /etc/httpd/conf.d/${FULLDOMAINNAME}.conf"


echo ""
echo "WebDAV is running."
echo "if hostname is accessible"
echo "                         http://${FULLDOMAINNAME}/${WEBDAV_ALIAS}"
echo "or if your domain is registered in DNS and has HTTPS enabled"
echo "                         https://${FULLDOMAINNAME}/${WEBDAV_ALIAS}"
echo ""

echo "Next Step - optional: Test your WebDAV instance with the 'cadaver' client:"
echo "  yum -y install cadaver"
echo "  cadaver http://localhost/${WEBDAV_ALIAS}"
echo "     or"
echo "  cadaver https://${FULLDOMAINNAME}/${WEBDAV_ALIAS}"

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-webdav/etc-httpd-confd/webdav.conf
