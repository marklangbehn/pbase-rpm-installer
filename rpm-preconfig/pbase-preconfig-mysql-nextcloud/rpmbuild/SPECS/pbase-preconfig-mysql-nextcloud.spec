Name: pbase-preconfig-mysql-nextcloud
Version: 1.0
Release: 3
Summary: PBase MySQL preconfigure rpm, preset user and DB name for use by pbase-nextcloud
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mysql-nextcloud-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mysql-nextcloud
Requires: pbase-php-transitive-dep, pbase-epel, pbase-preconfig-mysql80community, jq

%description
Configure MySQL preset user and DB name for use by pbase-nextcloud

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
#echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

## config is stored in json file with root-only permissions
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.json"
  PBASE_CONFIG_DIR="${PBASE_CONFIG_BASE}/module-config.d"

  ## config is stored in json file with root-only permissions
  ##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/

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

setFieldInJsonModuleConfig() {
  NEWVALUE="$1"
  MODULE="$2"
  FULLFIELDNAME="$3"
  MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"

  SOURCE_DIR="$4"
  if [[ "$SOURCE_DIR" == "" ]]; then
    SOURCE_DIR="$MODULE_CONFIG_DIR"
  fi

  CONFIG_FILE_NAME="${MODULE}.json"
  TEMPLATE_JSON_FILE="${SOURCE_DIR}/${CONFIG_FILE_NAME}"

  if [[ -e "${TEMPLATE_JSON_FILE}" ]] ; then
    /bin/cp -f "${TEMPLATE_JSON_FILE}" "/tmp/${CONFIG_FILE_NAME}"

    ## set a value in the json file
    PREFIX="jq '.${MODULE}.${FULLFIELDNAME}= \""
    SUFFIX="\"'"

    ## no quotes needed when setting boolean
    if [[ "${NEWVALUE}" == "true" ]] || [[ "${NEWVALUE}" == "false" ]] ; then
      PREFIX="jq '.${MODULE}.${FULLFIELDNAME}= "
      SUFFIX="'"
    fi

    JQ_COMMAND="${PREFIX}${NEWVALUE}${SUFFIX} /tmp/${CONFIG_FILE_NAME} > ${MODULE_CONFIG_DIR}/${CONFIG_FILE_NAME}"

    ##echo "Executing:  eval $JQ_COMMAND"
    eval $JQ_COMMAND

    /bin/rm -f "/tmp/${CONFIG_FILE_NAME}"
  else
    echo "Pre-config not present:   ${TEMPLATE_JSON_FILE}"
  fi
}

echo "PBase MySQL 8.0 community create config preset user and DB name for use by pbase-nextcloud"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

check_linux_version

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples"
DB_CONFIG_FILENAME="pbase_mysql80community.json"

PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for config file like "pbase_repo.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_EMAIL_ADDRESS" ".pbase_repo.defaultEmailAddress" ""
parseConfig "DEFAULT_SMTP_SERVER" ".pbase_repo.defaultSmtpServer" ""
parseConfig "DEFAULT_SMTP_USERNAME" ".pbase_repo.defaultSmtpUsername" ""
parseConfig "DEFAULT_SMTP_PASSWORD" ".pbase_repo.defaultSmtpPassword" ""
parseConfig "DEFAULT_SUB_DOMAIN" ".pbase_repo.defaultSubDomain" ""

## when DEFAULT_SUB_DOMAIN.txt file is not present
if [[ $DEFAULT_SUB_DOMAIN == null ]] ; then
  echo "No DEFAULT_SUB_DOMAIN override file found, using 'nextcloud' for defaultSubDomain"
  DEFAULT_SUB_DOMAIN="nextcloud"
fi
#echo "DEFAULT_SUB_DOMAIN:      ${DEFAULT_SUB_DOMAIN}"


## check if subdomain declared in pbase_repo.json needs to be updated
## handle case of new app running in a subdomain being overlaid on an existing apache running the root domain
## this is done by adding apache proxy instead of nginx proxy

PREVIOUS_SUB_DOMAIN="${DEFAULT_SUB_DOMAIN}"
DEFAULT_SUB_DOMAIN=""
PBASE_REPO_JSON_PATH="/usr/local/pbase-data/admin-only/module-config.d/pbase_repo.json"

if [[ -e "/root/DEFAULT_SUB_DOMAIN.txt" ]] ; then
  read -r DEFAULT_SUB_DOMAIN < /root/DEFAULT_SUB_DOMAIN.txt

  if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] && [[ "${PREVIOUS_SUB_DOMAIN}" == "" ]] ; then
    echo "Adding subdomain name:   pbase_repo.json"
    sed -i "s/defaultSubDomain\": null/defaultSubDomain\": \"${DEFAULT_SUB_DOMAIN}\"/" ${PBASE_REPO_JSON_PATH}
    sed -i "s/defaultSubDomain\": \"\"/defaultSubDomain\": \"${DEFAULT_SUB_DOMAIN}\"/" ${PBASE_REPO_JSON_PATH}
  fi
fi


## when smtp password was given, but not server then assume mailgun
if [[ "${DEFAULT_SMTP_SERVER}" == "" ]] && [[ "${DEFAULT_SMTP_PASSWORD}" != "" ]] ; then
  DEFAULT_SMTP_SERVER="smtp.mailgun.org"
fi


echo "Nextcloud config:        ${MODULE_CONFIG_DIR}/pbase_nextcloud.json"

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_apache.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_lets_encrypt.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_nextcloud.json  ${MODULE_CONFIG_DIR}/
## /bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_s3storage.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_smtp.json  ${MODULE_CONFIG_DIR}/

if [[ -e "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}" ]] ; then
  echo "Setting aside previous preconfig file: ${DB_CONFIG_FILENAME}"
  DATE_SUFFIX="$(date +'%Y-%m-%d_%H-%M')"
  mv "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}-PREV-${DATE_SUFFIX}.json"
fi

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${DB_CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/

echo "Let's Encrypt defaults:  ${MODULE_CONFIG_DIR}/pbase_lets_encrypt.json"

if [[ "${DEFAULT_EMAIL_ADDRESS}" != "" ]] ; then
  echo "emailAddress:            ${DEFAULT_EMAIL_ADDRESS}"
  setFieldInJsonModuleConfig ${DEFAULT_EMAIL_ADDRESS} pbase_lets_encrypt emailAddress
  setFieldInJsonModuleConfig ${DEFAULT_EMAIL_ADDRESS} pbase_apache serverAdmin
fi

QT="'"
DEFAULT_SUB_DOMAIN_QUOTED=${QT}${DEFAULT_SUB_DOMAIN}${QT}

if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] ; then
  echo "urlSubDomain:            ${DEFAULT_SUB_DOMAIN_QUOTED}"
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_lets_encrypt urlSubDomain
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_nextcloud urlSubDomain
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_apache urlSubDomain
  setFieldInJsonModuleConfig "false" pbase_apache enableCheckForWww
else
  echo "Setting empty urlSubDomain, Nextcloud will be root level of domain"
  echo "urlSubDomain:            ${DEFAULT_SUB_DOMAIN_QUOTED}"
  setFieldInJsonModuleConfig "" pbase_lets_encrypt urlSubDomain
  setFieldInJsonModuleConfig "" pbase_nextcloud urlSubDomain
  setFieldInJsonModuleConfig "" pbase_apache urlSubDomain
fi

echo "SMTP defaults:           ${MODULE_CONFIG_DIR}/pbase_smtp.json"

## replace domainname in smtp config template file
if [[ -e "${MODULE_CONFIG_DIR}/pbase_smtp.json" ]]; then
  sed -i "s/example.com/${THISDOMAINNAME}/" "${MODULE_CONFIG_DIR}/pbase_smtp.json"
fi

if [[ "${DEFAULT_SMTP_SERVER}" != "" ]] ; then
  echo "defaultSmtpServer:       ${DEFAULT_SMTP_SERVER}"
  setFieldInJsonModuleConfig ${DEFAULT_SMTP_SERVER} pbase_smtp server
fi

if [[ "${DEFAULT_SMTP_USERNAME}" != "" ]] ; then
  echo "defaultSmtpUsername:     ${DEFAULT_SMTP_USERNAME}"
  setFieldInJsonModuleConfig ${DEFAULT_SMTP_USERNAME} pbase_smtp login
fi

if [[ "${DEFAULT_SMTP_PASSWORD}" != "" ]] ; then
  echo "defaultSmtpPassword:     ${DEFAULT_SMTP_PASSWORD}"
  setFieldInJsonModuleConfig ${DEFAULT_SMTP_PASSWORD} pbase_smtp password
fi


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "Setting config with MySQL user and DB name for use by pbase-nextcloud"
echo "                         ${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"
#echo "Setting database 'rootPassword' and 'password' in ${DB_CONFIG_FILENAME}"
#echo "       for MySQL root:   $RAND_PW_ROOT"
#echo "       for nextcloud DB: $RAND_PW_USER"

## provide random password in database config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"
sed -i "s/SHOmeddata/${RAND_PW_ROOT}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"


echo ""
echo "MySQL, SMTP and Let's Encrypt module config files for Nextcloud added."
echo "Next step - optional - review the configuration defaults provided"
echo "    under 'module-config.d' by editing their JSON text files. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_apache.json"
echo "  vi ${DB_CONFIG_FILENAME}"
echo "  vi pbase_lets_encrypt.json"
echo "  vi pbase_smtp.json"
echo "  vi pbase_nextcloud.json"
echo ""

echo "Next step - install MySQL and Nextcloud application with:"
echo ""

if [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]] || [[ "${REDHAT_RELEASE_DIGIT}" == "9" ]] ; then
  echo "  yum -y --disablerepo=appstream install mysql-community-server"
fi

echo "  yum -y install pbase-mysql80community"
echo "  yum -y install pbase-nextcloud"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples/pbase_apache.json
/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples/pbase_lets_encrypt.json
/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples/pbase_mysql80community.json
/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples/pbase_nextcloud.json
/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples/pbase_s3storage.json
/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples/pbase_smtp.json
