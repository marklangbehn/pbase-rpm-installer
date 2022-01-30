Name: pbase-jellyfin
Version: 1.0
Release: 2
Summary: PBase Jellyfin service
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-jellyfin-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-jellyfin
Requires: pbase-apache, jellyfin-server, jellyfin-web, wget, jq, ffmpeg, ffmpeg-devel, SDL2, certbot, certbot-apache

%description
PBase Jellyfin service

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
  ## name of config file is passed in param $1 - for example "pbase_jellyfin.json"
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

echo "PBase Jellyfin service"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## check if already installed
#if [[ -d "/var/lib/jellyfin" ]]; then
#  echo "/var/lib/jellyfin directory already exists - exiting"
#  exit 0
#fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## Jellyfin config
## look for config file "pbase_jellyfin.json"
PBASE_CONFIG_FILENAME="pbase_jellyfin.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
## version to download
parseConfig "JELLYFIN_VER_CONFIG" ".pbase_jellyfin.jellyfinVersion" ""

parseConfig "HTTP_PORT" ".pbase_jellyfin.port" "8096"
parseConfig "ADD_APACHE_PROXY" ".pbase_jellyfin.addApacheProxy" "false"
parseConfig "URL_SUBPATH" ".pbase_jellyfin.urlSubPath" ""

echo "HTTP_PORT:               $HTTP_PORT"
echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"
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

## Check for /etc/httpd/conf.d/ssl.conf, comment it out if it exists
commentOutFile "/etc/httpd/conf.d" "ssl.conf"


## fetch previously registered domain names
DOMAIN_NAME_LIST=""
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"

echo "Existing domain names:   ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "Found domain-name-list:  ${DOMAIN_NAME_LIST}"


## check for subdomain
FULLDOMAINNAME="$THISDOMAINNAME"

## for Apache config choose either the ...subpath.conf or the ...subdomain.conf
##   depending on URL_SUBPATH and URL_SUBDOMAIN

PROXY_CONF_FILE="jellyfin-proxy-subpath.conf"
SUBPATH_URI=""

if [[ ${URL_SUBPATH} != "" ]] ; then
  SUBPATH_URI="/${URL_SUBPATH}"
  echo "Using SUBPATH_URI:       $SUBPATH_URI"
else
  PROXY_CONF_FILE="jellyfin-proxy-subdomain.conf"
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

echo ""
echo "${DOMAIN_NAME_LIST_NEW}" > ${SAVE_CMD_DIR}/domain-name-list.txt
echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "                         ${DOMAIN_NAME_LIST_NEW}"
echo ""

DOMAIN_NAME_LIST_HAS_WWW=$(grep www ${SAVE_CMD_DIR}/domain-name-list.txt)
##echo "Domain list has WWW:     ${DOMAIN_NAME_LIST_HAS_WWW}"

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

    ## set aside conf file so that certbot can recreate the ...le-ssl.conf
    if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" ]] ; then
      echo "Disabling prev conf:     /etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf"
      mv "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf-DISABLED"
    fi
  fi

  /bin/cp --no-clobber /usr/local/pbase-data/pbase-jellyfin/etc-httpd-confd/${PROXY_CONF_FILE} /etc/httpd/conf.d/

  mv -f "/etc/httpd/conf.d/${PROXY_CONF_FILE}" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

  if [[ ${URL_SUBDOMAIN} != "" ]] ; then
    echo "Setting subdomain:       ${CONF_FILE}"
    sed -i -e "s/jellyfin.example.com/${FULLDOMAINNAME}/" "${CONF_FILE}"
  else
    if [[ ${URL_SUBPATH} != "jellyfin" ]] ; then
      echo "Setting subpath:         ${CONF_FILE}"
      sed -i -e "s/jellyfin.example.com/${FULLDOMAINNAME}/" "${CONF_FILE}"
      sed -i -e "s|/jellyfin http|/${URL_SUBPATH} http|" "${CONF_FILE}"
    fi

    ## may also enable www alias
    sed -i "s/www.example.com/www.${THISDOMAINNAME}/" "${CONF_FILE}"
    sed -i "s/example.com/${THISDOMAINNAME}/" "${CONF_FILE}"

    if [[ "${DOMAIN_NAME_LIST_HAS_WWW}" != "" ]] ; then
      echo "Enabling:                ServerAlias www.${THISDOMAINNAME}"
      sed -i "s/#ServerAlias/ServerAlias/" "${CONF_FILE}"
    fi
  fi


  echo ""
  echo "Starting service:        /etc/systemd/system/jellyfin"
  systemctl daemon-reload
  systemctl enable jellyfin

  systemctl start jellyfin
  systemctl status jellyfin


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

  echo "Jellyfin service running at this URL:"
  echo "                         http://${FULLDOMAINNAME}${SUBPATH_URI}"
else
  echo "Starting service:        /etc/systemd/system/jellyfin"
  systemctl daemon-reload
  systemctl enable jellyfin
  systemctl start jellyfin
  systemctl status jellyfin

  echo "Jellyfin service running on port 8096 at this URL:"
  echo "                         http://localhost:8096"
fi

## add shell aliases
append_bashrc_alias editjellyfinconf "vi /etc/jellyfin/system.xml"
append_bashrc_alias stopjellyfin "/bin/systemctl stop jellyfin"
append_bashrc_alias startjellyfin "/bin/systemctl start jellyfin"
append_bashrc_alias statusjellyfin "/bin/systemctl status jellyfin"
append_bashrc_alias restartjellyfin "/bin/systemctl restart jellyfin"
append_bashrc_alias tailjellyfin "journalctl -xf -u jellyfin"

## REVISIT configure log filename somehow
## append_bashrc_alias tailjellyfin "tail -f /var/log/jellyfin/log_20210603.log"


echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-jellyfin/etc-httpd-confd/jellyfin-proxy-subdomain.conf
/usr/local/pbase-data/pbase-jellyfin/etc-httpd-confd/jellyfin-proxy-subpath.conf
