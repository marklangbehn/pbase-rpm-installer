Name: pbase-owncloud
Version: 1.0
Release: 1
Summary: PBase ownCloud oCIS rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-owncloud-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-owncloud
Requires: pbase-lets-encrypt-transitive-dep, jq, certbot, pbase-firewall-enable

%description
PBase ownCloud oCIS service

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
  ## name of config file is passed in param $1 - for example "pbase_owncloud.json"
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

echo "PBase ownCloud oCIS install"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## check if already installed
if [[ -e "/usr/local/bin/ocis" ]]; then
  echo "/usr/local/bin/ocis already exists - exiting"
  exit 0
fi


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

## ownCloud oCIS download from repo
DOWNLOAD_URL="https://download.owncloud.com/ocis/ocis/stable/2.0.0/ocis-2.0.0-linux-amd64"
USE_DOWNLOAD_URL=false

## ownCloud oCIS config
## look for config file "pbase_owncloud.json"
PBASE_CONFIG_FILENAME="pbase_owncloud.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "AUTO_OCIS_INIT" ".pbase_owncloud.autoOcisInit" "true"
parseConfig "ENABLE_AUTORENEW" ".pbase_owncloud.enableAutoRenew" "true"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_owncloud.executeCertbotCmd" "true"
parseConfig "DOWNLOAD_URL" ".pbase_owncloud.downloadUrl" "https://download.owncloud.com/ocis/ocis/stable/2.0.0/ocis-2.0.0-linux-amd64"
parseConfig "CUSTOM_DOWNLOAD_URL" ".pbase_owncloud.customDownloadUrl" "https://download.owncloud.com/ocis/ocis/daily/ocis-testing-linux-amd64"
parseConfig "USE_CUSTOM_DOWNLOAD_URL" ".pbase_owncloud.useCustomDownloadUrl" "false"

parseConfig "URL_SUBDOMAIN" ".pbase_owncloud.urlSubDomain" "owncloud"
parseConfig "EMAIL_ADDR" ".pbase_owncloud.emailAddress" "yoursysadmin@yourrealmail.com"
parseConfig "OCIS_USERNAME" ".pbase_owncloud.ocisUsername" "ocis"
parseConfig "ADMIN_PASSWORD" ".pbase_owncloud.adminPassword" ""

echo "AUTO_OCIS_INIT:          $AUTO_OCIS_INIT"
echo "ENABLE_AUTORENEW:        $ENABLE_AUTORENEW"
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
echo "OCIS_USERNAME:           $OCIS_USERNAME"
echo "ADMIN_PASSWORD:          $ADMIN_PASSWORD"

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

#echo "Found DOMAIN_NAME_LIST:  ${DOMAIN_NAME_LIST}"

if [[ "${DOMAIN_NAME_LIST}" == "" ]] ; then
  #echo "Starting from empty domain-name-list.txt, adding ${FULLDOMAINNAME}"
  DOMAIN_NAME_LIST_NEW="${FULLDOMAINNAME}"
  DOMAIN_NAME_PARAM="${FULLDOMAINNAME}"
else
    ## use cut to grab first name from comma delimited list
    FIRSTDOMAINNREGISTERED=$(cut -f1 -d "," ${SAVE_CMD_DIR}/domain-name-list.txt)
    ##echo "FIRSTDOMAINNREGISTERED:  ${FIRSTDOMAINNREGISTERED}"

  if [[ "${DOMAIN_NAME_LIST}" == *"${FULLDOMAINNAME}"* ]]; then
    #echo "Already has ${FULLDOMAINNAME}"
    DOMAIN_NAME_LIST_NEW="${DOMAIN_NAME_LIST}"
    DOMAIN_NAME_PARAM="${DOMAIN_NAME_LIST}"
  else
    #echo "Adding ${FULLDOMAINNAME}"
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

if [[ "${USE_CUSTOM_DOWNLOAD_URL}" == "true" ]] ; then
  echo "Using customDownloadUrl: ${CUSTOM_DOWNLOAD_URL}"
  DOWNLOAD_URL="${CUSTOM_DOWNLOAD_URL}"
fi

echo "Downloading from:        ${DOWNLOAD_URL}"
wget -q -O /usr/local/bin/ocis ${DOWNLOAD_URL}

## make sure file got downloaded
if [[ ! -e "/usr/local/bin/ocis" ]] ; then
  echo "Could not download ownCloud oCIS from URL: ${DOWNLOAD_URL}"
  exit 1
fi

echo "ownCloud oCIS binary:"
chmod +x /usr/local/bin/ocis
ls -lh /usr/local/bin/ocis
echo ""

echo "Enabling port < 1024:    setcap cap_net_bind_service=+eip /usr/local/bin/ocis"
setcap cap_net_bind_service=+eip /usr/local/bin/ocis

echo "Creating directory:      /etc/ocis"
mkdir -p /etc/ocis
#chown -R ocis /etc/ocis
chmod 0570 /etc/ocis

echo "Setting .env file:       /etc/ocis/ocis.env"
/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-owncloud/etc-ocis/ocis.env /etc/ocis/ocis.env

sed -i -e "s/owncloud.example.com/${FULLDOMAINNAME}/" /etc/ocis/ocis.env
sed -i -e "s/example.com/${THISDOMAINNAME}/" /etc/ocis/ocis.env

echo "Creating group and user: ocis"

adduser \
   --system \
   --shell /bin/bash \
   --comment 'oCIS user' \
   --user-group \
   --home /home/ocis -m \
   ocis


## add ocis service file
echo "systemd service:         /etc/systemd/system/ocis.service"
/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-owncloud/etc-systemd-system/ocis.service /etc/systemd/system/ocis.service


## LETS ENCRYPT - HTTPS CERTIFICATE
CERTBOT_CMD="certbot certonly --standalone --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"

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

## add symlinks to let ocis user access the certificate files under /etc/letsencrypt
if [[ -d /etc/letsencrypt ]] ; then
  chmod a+rx /etc/letsencrypt/archive/
  chmod a+rx /etc/letsencrypt/live/
  
  ## allow read of privkey1.pem from ocis 
  chmod a+r /etc/letsencrypt/archive/${FULLDOMAINNAME}/*.pem
  
  cd /home/ocis
  ln -s "/etc/letsencrypt/live/${FULLDOMAINNAME}/privkey.pem" /home/ocis/privkey.pem
  ln -s "/etc/letsencrypt/live/${FULLDOMAINNAME}/cert.pem" /home/ocis/cert.pem
  
  ls -la /home/ocis/*.pem
  echo ""
fi


## start auto renew timer
if [[ $ENABLE_AUTORENEW == "true" ]]; then
  if [[ -e "/usr/lib/systemd/system/certbot-renew.timer" ]] ; then
    echo "Enabling auto renew:     /usr/lib/systemd/system/certbot-renew.timer"
    
    /bin/systemctl enable certbot-renew.timer
    /bin/systemctl start certbot-renew.timer
    /bin/systemctl status certbot-renew.timer
  else
    ## when systemd timer does not exist use cron instead 
    echo "Adding cron jobs:        /etc/crontab"
    ## create empty log file
    CRONJOB_LOGFILE="/var/log/letsencrypt-sslrenew.log"
    touch "$CRONJOB_LOGFILE"
    chown root:root ${CRONJOB_LOGFILE}
    ## run tasks at random minute - under 0:50, random hour before 11pm
    RAND_MINUTE="$((2 + RANDOM % 50))"
    RAND_HOUR="$((2 + RANDOM % 23))"
    
    CRONJOB_LINE1="${RAND_MINUTE} ${RAND_HOUR} * * * root /usr/bin/certbot renew --deploy-hook '/bin/systemctl restart ocis' >> $CRONJOB_LOGFILE"
    echo ""  >>  /etc/crontab
    echo "## Added by pbase-owncloud RPM ##"  >>  /etc/crontab
    echo "$CRONJOB_LINE1"  >>  /etc/crontab
  fi
else
  echo "Auto renew unchanged:    enableAutoRenew=false"
fi


## add shell aliases
append_bashrc_alias tailocis "journalctl -l -u ocis -f"
append_bashrc_alias journalocis "journalctl -u ocis -f"

append_bashrc_alias editocisservice "vi /etc/systemd/system/ocis.service"

append_bashrc_alias stopocis "/bin/systemctl stop ocis"
append_bashrc_alias startocis "/bin/systemctl start ocis"
append_bashrc_alias statusocis "/bin/systemctl status ocis"
append_bashrc_alias restartocis "/bin/systemctl restart ocis"


/bin/systemctl daemon-reload
/bin/systemctl enable ocis

if [[ $AUTO_OCIS_INIT == "true" ]]; then
  OCIS_INIT_CMD="ocis init --insecure yes"
  
  ## add adminPassword if it is non-empty in pbase_owncloud.json config
  if [[ "${ADMIN_PASSWORD}" != "" ]] ; then
    OCIS_INIT_CMD="${OCIS_INIT_CMD} --admin-password ${ADMIN_PASSWORD}"
  fi
  
  echo "Calling:                 ${OCIS_INIT_CMD}"
  su - ocis -c "${OCIS_INIT_CMD}"

  echo "Starting ocis service:  /etc/systemd/system/ocis.service"
  /bin/systemctl start ocis
  /bin/systemctl status ocis
else
  echo "Next Steps - REQUIRED - as the 'ocis' user manually execute 'ocis init' command, then do 'systemctl start ocis'"
  echo "                        then do 'systemctl start ocis'"
  echo "  su - ocis"
  echo "  ocis init"
  echo "  exit"
  echo "  systemctl start ocis"
  echo "  journalctl -u ocis -f"
fi

EXTERNALURL="https://$FULLDOMAINNAME"
echo "ownCloud oCIS installed:         $EXTERNALURL"
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-owncloud/etc-systemd-system/ocis.service
/usr/local/pbase-data/pbase-owncloud/etc-ocis/ocis.env
/usr/local/pbase-data/pbase-owncloud/etc-ocis/ocis-localhost.env
