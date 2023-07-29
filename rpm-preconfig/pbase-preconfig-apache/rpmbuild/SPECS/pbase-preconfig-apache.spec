Name: pbase-preconfig-apache
Version: 1.0
Release: 2
Summary: PBase Apache httpd config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-apache-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-apache
Requires: jq

%description
Add Apache httpd pre-config file

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase Apache httpd pre-config file create"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi


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
  if [[ ! -e "${TEMPLATE_JSON_FILE}" ]] ; then
    echo "Bypassing set field in: ${MODULE}"
    return 1
  fi
  
  /bin/cp -f "${TEMPLATE_JSON_FILE}" "/tmp/${CONFIG_FILE_NAME}"

  ## set a value in the json file
  PREFIX="jq '.${MODULE}.${FULLFIELDNAME}= \""
  SUFFIX="\"'"
  JQ_COMMAND="${PREFIX}${NEWVALUE}${SUFFIX} /tmp/${CONFIG_FILE_NAME} > ${MODULE_CONFIG_DIR}/${CONFIG_FILE_NAME}"

  ##echo "Executing:  eval $JQ_COMMAND"
  eval $JQ_COMMAND

  /bin/rm -f "/tmp/${CONFIG_FILE_NAME}"
}

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-apache/module-config-samples"

PBASE_DEFAULTS_FILENAME="pbase_repo.json"
PBASE_REPO_JSON_PATH="${MODULE_CONFIG_DIR}/${PBASE_DEFAULTS_FILENAME}"

## look for config file like "pbase_repo.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_EMAIL_ADDRESS" ".pbase_repo.defaultEmailAddress" ""
parseConfig "DEFAULT_SUB_DOMAIN" ".pbase_repo.defaultSubDomain" ""


## when subdomain text file exists, change 'null' literal to an empty string
## needed to do subdomain substitution later

if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] || [[ $DEFAULT_EMAIL_ADDRESS != "" ]]; then
  echo "Copying preconfig:       pbase_apache.json"
  /bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_apache.json  ${MODULE_CONFIG_DIR}/
fi

## when DEFAULT_SUB_DOMAIN.txt file is not present
if [[ $DEFAULT_SUB_DOMAIN == null ]] ; then
  echo "No DEFAULT_SUB_DOMAIN override file found, using '' for defaultSubDomain"
  DEFAULT_SUB_DOMAIN=""
fi

if [[ -e /root/DEFAULT_SUB_DOMAIN.txt ]] ; then
  read -r DEFAULT_SUB_DOMAIN < /root/DEFAULT_SUB_DOMAIN.txt
  sed -i "s/defaultSubDomain\": null/defaultSubDomain\": \"\"/" ${PBASE_REPO_JSON_PATH}
  ##echo "DEFAULT_SUB_DOMAIN:    ${DEFAULT_SUB_DOMAIN}"
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_repo urlSubDomain
fi

QT="'"
DEFAULT_SUB_DOMAIN_QUOTED=${QT}${DEFAULT_SUB_DOMAIN}${QT}
echo "DEFAULT_SUB_DOMAIN:      ${DEFAULT_SUB_DOMAIN_QUOTED}"

if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] ; then
  echo "urlSubDomain:            ${DEFAULT_SUB_DOMAIN_QUOTED}"
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_apache urlSubDomain
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_lets_encrypt urlSubDomain
else
  echo "Setting empty urlSubDomain, Apache will be root level of domain"
  setFieldInJsonModuleConfig "" pbase_apache urlSubDomain
  setFieldInJsonModuleConfig "" pbase_lets_encrypt urlSubDomain
fi


## when email is defined in pbase_repo.json use that to provide the Apache httpd.conf email address
if [[ $DEFAULT_EMAIL_ADDRESS != "" ]]; then
  echo "Setting 'defaultEmailAddress' in pbase_apache.json"
  echo "                         ${DEFAULT_EMAIL_ADDRESS}"
  sed -i "s/yoursysadmin@yourrealmail.com/${DEFAULT_EMAIL_ADDRESS}/" "${MODULE_CONFIG_DIR}/pbase_apache.json"

  echo ""
  echo "Next step - optional - review the Apache server default config by"
  echo "    editing the pbase_apache.json file. For example:"
  echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
else
  echo ""
  echo "Next step - optional - change the Apache server default config by"
  echo "    making a copy of the config sample file and editing it. For example:"
  echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
  echo "  cp ${MODULE_SAMPLES_DIR}/pbase_apache.json ."
fi

echo "  vi pbase_apache.json"
echo ""
echo "Next step - install Apache with:"
echo ""
echo "  yum -y install pbase-apache"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-apache/module-config-samples/pbase_apache.json
