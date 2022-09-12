Name: pbase-minio
Version: 1.0
Release: 1
Summary: PBase Minio service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-minio-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-minio
Requires: unzip, wget, jq

%description
PBase Minio service

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
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
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

echo "PBase Minio service"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## check if already installed
if [[ -e "/usr/local/bin/minio" ]]; then
  echo "Minio executable /usr/local/bin/minio already exists - exiting"
  exit 0
fi

check_linux_version


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## Minio config
## look for config file "pbase_minio.json"
PBASE_CONFIG_FILENAME="pbase_minio.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "MINIO_VOLUMES" ".pbase_minio.minioVolumes" "/opt/minio/data"
parseConfig "MINIO_OPTS" ".pbase_minio.minioOpts" ""
parseConfig "MINIO_ACCESS_KEY" ".pbase_minio.minioAccessKey" ""
parseConfig "MINIO_SECRET_KEY" ".pbase_minio.minioSecretAccessKey" ""
parseConfig "MINIO_REGION_NAME" ".pbase_minio.minioRegionName" ""

parseConfig "HTTP_PORT" ".pbase_minio.port" "9000"
parseConfig "ADD_APACHE_PROXY" ".pbase_minio.addApacheProxy" "true"
parseConfig "URL_SUBDOMAIN" ".pbase_minio.urlSubDomain" "minio"

echo "MINIO_VOLUMES:           ${MINIO_VOLUMES}"
echo "MINIO_OPTS:              ${MINIO_OPTS}"
echo "MINIO_ACCESS_KEY:        ${MINIO_ACCESS_KEY}"
echo "MINIO_SECRET_KEY:        ${MINIO_SECRET_KEY}"
echo "MINIO_REGION_NAME:       ${MINIO_REGION_NAME}"

echo "HTTP_PORT:               ${HTTP_PORT}"
echo "ADD_APACHE_PROXY:        ${ADD_APACHE_PROXY}"
echo "URL_SUBDOMAIN:           ${URL_SUBDOMAIN}"


PBASE_CONFIG_FILENAME="pbase_lets_encrypt.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "CONFIG_ENABLE_AUTORENEW" ".pbase_lets_encrypt.enableAutoRenew" "true"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_lets_encrypt.executeCertbotCmd" "true"

parseConfig "EMAIL_ADDR" ".pbase_lets_encrypt.emailAddress" "yoursysadmin@yourrealmail.com"

echo "CONFIG_ENABLE_AUTORENEW: $CONFIG_ENABLE_AUTORENEW"
echo "EXECUTE_CERTBOT_CMD:     $EXECUTE_CERTBOT_CMD"
echo "EMAIL_ADDR:              $EMAIL_ADDR"

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

echo "Existing domain names:   ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "Found domain-name-list:  ${DOMAIN_NAME_LIST}"


## check for subdomain
FULLDOMAINNAME="$THISDOMAINNAME"

## for Apache config choose either the ...subpath.conf or the ...subdomain.conf
##   depending on URL_SUBPATH and URL_SUBDOMAIN

PROXY_CONF_FILE="minio-vhost.conf"

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

echo "FULLDOMAINNAME:          $FULLDOMAINNAME"
echo "PROXY_CONF_FILE:         $PROXY_CONF_FILE"

echo "Creating user:           minio"

groupadd --system minio
useradd -s /sbin/nologin --system -g minio minio

echo "Data directory:          /opt/minio/data"

mkdir -p /opt/minio/data
chown -R minio:minio /opt/minio


cd /usr/local/bin
echo "Downloading Minio server binary"

wget -q https://dl.minio.io/server/minio/release/linux-amd64/minio
chmod +x minio

echo "Downloading Minio client binary"

wget -q https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc


echo "Downloaded files from min.io"
ls -lh /usr/local/bin/minio
ls -lh /usr/local/bin/mc

echo "Config file:             /etc/default/minio.conf"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-minio/etc-default/minio.conf /etc/default/


echo "Service:                 /etc/systemd/system/minio.service"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-minio/etc-systemd-system/minio.service /etc/systemd/system/


systemctl daemon-reload
systemctl enable minio
systemctl start minio

systemctl status minio


if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then
  ## must install apache first
  if [[ ! -d "/etc/httpd/conf.d/" ]] ; then
    echo "Apache not found:        /etc/httpd/conf.d/"
    exit 0
  fi

  ## set aside previous .conf and ...le-ssl.conf files for this domain
  PREV_CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  if [[ -e "${PREV_CONF_FILE}" ]] ; then
    echo "Disabling previous:      ${PREV_CONF_FILE}"
    mv "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf-DISABLED"

    if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" ]] ; then
      mv "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf-DISABLED"
    fi
  fi

  /bin/cp --no-clobber /usr/local/pbase-data/pbase-minio/etc-httpd-confd/${PROXY_CONF_FILE} /etc/httpd/conf.d/

  mv -f "/etc/httpd/conf.d/${PROXY_CONF_FILE}" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

  if [[ ${URL_SUBDOMAIN} != "" ]] ; then
    echo "Setting subdomain:       ${CONF_FILE}"
    sed -i -e "s/subdomain.example.com/${FULLDOMAINNAME}/" "${CONF_FILE}"
  else
    sed -i -e "s/subdomain.example.com/${THISDOMAINNAME}/" "${CONF_FILE}"

    ## may also enable www alias
    sed -i "s/www.example.com/www.${THISDOMAINNAME}/" "${CONF_FILE}"
    sed -i "s/example.com/${THISDOMAINNAME}/" "${CONF_FILE}"
  fi

  echo ""
  echo "Restarting httpd"
  systemctl restart httpd

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

  echo "Minio service running at this URL:"
  echo "                         http://${FULLDOMAINNAME}"
  echo "  or"
  echo "                         https://${FULLDOMAINNAME}"
else
  echo "Minio service running on port 9000 at this URL:"
  echo "                         http://{FULLDOMAINNAME}:8096"
fi

echo "Minio install complete"

## add shell aliases
append_bashrc_alias tailminio "journalctl -fu minio.service"
append_bashrc_alias editminioconf "vi /etc/default/minio.conf"

append_bashrc_alias stopminio "/bin/systemctl stop minio"
append_bashrc_alias startminio "/bin/systemctl start minio"
append_bashrc_alias statusminio "/bin/systemctl status minio"
append_bashrc_alias restartminio "/bin/systemctl restart minio"


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-minio/etc-default/minio.conf
/usr/local/pbase-data/pbase-minio/etc-httpd-confd/minio-vhost.conf
/usr/local/pbase-data/pbase-minio/etc-systemd-system/minio.service
