Name: pbase-preconfig-webdav
Version: 1.0
Release: 0
Summary: PBase Apache WebDAV config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-webdav-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-webdav
Requires: jq

%description
Add Apache WebDAV pre-config file

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
echo "rpm postinstall $1"

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
    echo "Pre-config not present:  ${TEMPLATE_JSON_FILE}"
  fi
}

echo "PBase WebDAV Apache httpd pre-config file create"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-webdav/module-config-samples"

PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for config file like "pbase_repo.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_EMAIL_ADDRESS" ".pbase_repo.defaultEmailAddress" ""
parseConfig "DEFAULT_DESKTOP_USERNAME" ".pbase_repo.defaultDesktopUsername" ""
parseConfig "DEFAULT_SUB_DOMAIN" ".pbase_repo.defaultSubDomain" ""

## when DEFAULT_SUB_DOMAIN.txt file is not present
if [[ $DEFAULT_SUB_DOMAIN == null ]] ; then
  echo "No DEFAULT_SUB_DOMAIN override file found, using '' for defaultSubDomain"
  DEFAULT_SUB_DOMAIN=""
fi
#echo "DEFAULT_SUB_DOMAIN:      ${DEFAULT_SUB_DOMAIN}"


## check if subdomain declared in pbase_repo.json needs to be updated
## handle case of new app running in a subdomain being overlaid on an existing apache running the root domain
## this is done by adding apache proxy instead of nginx proxy

PREVIOUS_SUB_DOMAIN="${DEFAULT_SUB_DOMAIN}"
DEFAULT_SUB_DOMAIN=""
DEFAULT_DESKTOP_USERNAME=""

PBASE_REPO_JSON_PATH="/usr/local/pbase-data/admin-only/module-config.d/pbase_repo.json"
PBASE_LETS_ENCRYPT_JSON_PATH="/usr/local/pbase-data/admin-only/module-config.d/pbase_lets_encrypt.json"

if [[ -e "/root/DEFAULT_SUB_DOMAIN.txt" ]] ; then
  read -r DEFAULT_SUB_DOMAIN < /root/DEFAULT_SUB_DOMAIN.txt

  if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] && [[ "${PREVIOUS_SUB_DOMAIN}" == "" ]] ; then
    echo "Adding subdomain name:   pbase_repo.json"
    sed -i "s/defaultSubDomain\": null/defaultSubDomain\": \"${DEFAULT_SUB_DOMAIN}\"/" ${PBASE_REPO_JSON_PATH}
    sed -i "s/defaultSubDomain\": \"\"/defaultSubDomain\": \"${DEFAULT_SUB_DOMAIN}\"/" ${PBASE_REPO_JSON_PATH}
  fi
fi


if [[ -e /root/DEFAULT_DESKTOP_USERNAME.txt ]] ; then
  read -r DEFAULT_DESKTOP_USERNAME < /root/DEFAULT_DESKTOP_USERNAME.txt
fi

echo "Setting pbase_webdav.json"
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_webdav.json  ${MODULE_CONFIG_DIR}/


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
echo "    basicAuthUsername:   $DEFAULT_DESKTOP_USERNAME"
echo "    basicAuthPassword:   $RAND_PW_USER"

## set webdav user to name given for defaultDesktopUsername
setFieldInJsonModuleConfig ${DEFAULT_DESKTOP_USERNAME} pbase_webdav basicAuthUsername

## provide random password in database config file
setFieldInJsonModuleConfig ${RAND_PW_USER} pbase_webdav basicAuthPassword


## when email is defined in pbase_repo.json use that to provide the Apache httpd.conf email address
if [[ $DEFAULT_EMAIL_ADDRESS != "" ]]; then
  echo "Setting 'defaultEmailAddress' in pbase_apache.json"
  echo "                         ${DEFAULT_EMAIL_ADDRESS}"
  /bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_apache.json  ${MODULE_CONFIG_DIR}/
  sed -i "s/yoursysadmin@yourrealmail.com/${DEFAULT_EMAIL_ADDRESS}/" "${MODULE_CONFIG_DIR}/pbase_apache.json"

  QT="'"
  DEFAULT_SUB_DOMAIN_QUOTED=${QT}${DEFAULT_SUB_DOMAIN}${QT}
  ##echo "DEFAULT_SUB_DOMAIN:      ${DEFAULT_SUB_DOMAIN_QUOTED}"

  if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] ; then
    echo "urlSubDomain:            ${DEFAULT_SUB_DOMAIN_QUOTED}"
    setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_lets_encrypt urlSubDomain
    setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_apache urlSubDomain
    setFieldInJsonModuleConfig "false" pbase_lets_encrypt enableCheckForWww
    setFieldInJsonModuleConfig "false" pbase_apache enableCheckForWww
  else
    echo "Setting empty urlSubDomain, Apache will be root level of domain"
    setFieldInJsonModuleConfig "" pbase_apache urlSubDomain
  fi

  echo ""
  echo "Next step - optional - review the Apache and WebDAV server default config by"
  echo "    editing the pbase_webdav.json file. For example:"
  echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
else
  echo ""
  echo "Next step - optional - change the Apache server default config by"
  echo "    making a copy of the config sample file and editing it. For example:"
  echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
  echo "  cp ${MODULE_SAMPLES_DIR}/pbase_webdav.json ."
fi

echo "  vi pbase_webdav.json"
echo ""
echo "Next step - install Apache WebDAV with:"
echo ""
echo "  yum -y install pbase-webdav"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-webdav/module-config-samples/pbase_apache.json
/usr/local/pbase-data/pbase-preconfig-webdav/module-config-samples/pbase_webdav.json
