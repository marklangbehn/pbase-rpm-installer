Name: activpb-preconfig-postgres-peertube
Version: 1.0
Release: 0
Summary: PBase Postgres preconfigure rpm, preset user and DB name for use by activpb-peertube
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: activpb-preconfig-postgres-peertube-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: activpb-preconfig-postgres-peertube
Requires: pbase-preconfig-yarn, pbase-epel, jq, pbase-rpmfusion

%description
Configure Postgres preset user and DB name for use by activpb-peertube

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


check_linux_version() {
  AMAZON1_RELEASE=""
  AMAZON2_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2')"
    echo "system-release:          ${SYSTEM_RELEASE}"
  fi

  FEDORA_RELEASE=""
  if [[ -e "/etc/fedora-release" ]]; then
    FEDORA_RELEASE="$(cat /etc/fedora-release)"
    echo "fedora_release:          ${FEDORA_RELEASE}"
  fi

  REDHAT_RELEASE_DIGIT=""
  if [[ -e "/etc/redhat-release" ]]; then
    REDHAT_RELEASE_DIGIT="$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n1)"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "AMAZON1_RELEASE:         $AMAZON1_RELEASE"
    REDHAT_RELEASE_DIGIT="6"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON2_RELEASE" != "" ]]; then
    echo "AMAZON2_RELEASE:         $AMAZON2_RELEASE"
    REDHAT_RELEASE_DIGIT="7"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
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
  /bin/cp -f "${TEMPLATE_JSON_FILE}" "/tmp/${CONFIG_FILE_NAME}"

  ## set a value in the json file
  PREFIX="jq '.${MODULE}.${FULLFIELDNAME}= \""
  SUFFIX="\"'"
  JQ_COMMAND="${PREFIX}${NEWVALUE}${SUFFIX} /tmp/${CONFIG_FILE_NAME} > ${MODULE_CONFIG_DIR}/${CONFIG_FILE_NAME}"

  ##echo "Executing:  eval $JQ_COMMAND"
  eval $JQ_COMMAND

  /bin/rm -f "/tmp/${CONFIG_FILE_NAME}"
}

echo "PBase Postgres create config preset user and DB name for use by activpb-peertube"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/activpb-preconfig-postgres-peertube/module-config-samples"

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
  echo "No DEFAULT_SUB_DOMAIN override file found, using 'peertube' for defaultSubDomain"
  DEFAULT_SUB_DOMAIN="peertube"
fi
#echo "DEFAULT_SUB_DOMAIN:      ${DEFAULT_SUB_DOMAIN}"


## when smtp password was given, but not server then assume mailgun
if [[ "${DEFAULT_SMTP_SERVER}" == "" ]] && [[ "${DEFAULT_SMTP_PASSWORD}" != "" ]] ; then
  DEFAULT_SMTP_SERVER="smtp.mailgun.org"
fi


DB_CONFIG_FILENAME="pbase_postgres.json"

echo "Peertube config:         ${MODULE_CONFIG_DIR}/activpb_peertube.json"
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_lets_encrypt.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/activpb_peertube.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_smtp.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_postgres.json  ${MODULE_CONFIG_DIR}/

echo "Let's Encrypt defaults:  ${MODULE_CONFIG_DIR}/pbase_lets_encrypt.json"

if [[ "${DEFAULT_EMAIL_ADDRESS}" != "" ]] ; then
  echo "emailAddress:            ${DEFAULT_EMAIL_ADDRESS}"
  setFieldInJsonModuleConfig ${DEFAULT_EMAIL_ADDRESS} pbase_lets_encrypt emailAddress
fi

QT="'"
DEFAULT_SUB_DOMAIN_QUOTED=${QT}${DEFAULT_SUB_DOMAIN}${QT}

echo "DEFAULT_SUB_DOMAIN:      ${DEFAULT_SUB_DOMAIN_QUOTED}"

if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] ; then
  echo "urlSubDomain:            ${DEFAULT_SUB_DOMAIN}"
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_lets_encrypt urlSubDomain
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} activpb_peertube urlSubDomain
else
  echo "Setting empty urlSubDomain, Peertube will be root level of domain"
  setFieldInJsonModuleConfig "" pbase_lets_encrypt urlSubDomain
  setFieldInJsonModuleConfig "" activpb_peertube urlSubDomain
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
echo "RAND_PW_USER:            $RAND_PW_USER"

## provide random password in database config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

## provide domainname in smtp config file
sed -i "s/example.com/${THISDOMAINNAME}/" "${MODULE_CONFIG_DIR}/pbase_smtp.json"


echo ""
echo "Postgres, SMTP and Let's Encrypt module config files for Peertube added."
echo "Next step - optional - review the configuration defaults provided"
echo "    under 'module-config.d' by editing their JSON text files. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_lets_encrypt.json"
echo "  vi pbase_postgres.json"
echo "  vi pbase_smtp.json"
echo "  vi activpb_peertube.json"
echo ""

echo "Next step - install Postgres and Peertube application with:"
echo "  yum -y install pbase-postgres"
echo "  yum -y install activpb-peertube"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/activpb-preconfig-postgres-peertube/module-config-samples/activpb_peertube.json
/usr/local/pbase-data/activpb-preconfig-postgres-peertube/module-config-samples/pbase_lets_encrypt.json
/usr/local/pbase-data/activpb-preconfig-postgres-peertube/module-config-samples/pbase_postgres.json
/usr/local/pbase-data/activpb-preconfig-postgres-peertube/module-config-samples/pbase_s3storage.json
/usr/local/pbase-data/activpb-preconfig-postgres-peertube/module-config-samples/pbase_smtp.json
