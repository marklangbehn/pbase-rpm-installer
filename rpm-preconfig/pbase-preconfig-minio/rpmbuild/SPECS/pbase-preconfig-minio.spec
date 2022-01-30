Name: pbase-preconfig-minio
Version: 1.0
Release: 1
Summary: PBase Minio config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-minio-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-minio
Requires: pbase-epel, jq

%description
Configure Minio server dependencies and config file

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

echo "PBase Minio dependencies and pre-config"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-minio/module-config-samples"

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


CONFIG_FILENAME="pbase_minio.json"

echo "Minio storage config:    ${MODULE_CONFIG_DIR}/${CONFIG_FILENAME}"

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
echo "  minioAccessKey:        $DEFAULT_DESKTOP_USERNAME"
echo "  minioSecretAccessKey:  $RAND_PW_USER"

## set webdav user to name given for defaultDesktopUsername
setFieldInJsonModuleConfig ${DEFAULT_DESKTOP_USERNAME} pbase_minio minioAccessKey

## provide random password for minio user
setFieldInJsonModuleConfig ${RAND_PW_USER} pbase_minio minioSecretAccessKey

## set the subdomain name
setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_minio urlSubDomain


echo ""
echo "Next step - required - customize the Minio configuration defaults provided"
echo "    under 'module-config.d' by editing the JSON text file. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi ${CONFIG_FILENAME}"
echo ""
echo "Next step - finish Minio server install with:"
echo ""
echo "  yum -y install pbase-minio"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-minio/module-config-samples/pbase_minio.json
