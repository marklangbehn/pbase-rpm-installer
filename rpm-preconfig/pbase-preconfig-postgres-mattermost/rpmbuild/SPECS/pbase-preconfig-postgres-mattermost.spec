Name: pbase-preconfig-postgres-mattermost
Version: 1.0
Release: 4
Summary: PBase Postgres preconfigure rpm, preset user and DB name for use by pbase-mattermost
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-postgres-mattermost-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-postgres-mattermost
Requires: pbase-epel, jq, pbase-preconfig-firewall-enable

%description
Configure Postgres preset user and DB name for use by pbase-mattermost

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

echo "PBase Postgres create config preset user and DB name for use by pbase-mattermost"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples"

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
  echo "No DEFAULT_SUB_DOMAIN override file found, using 'mattermost' for defaultSubDomain"
  DEFAULT_SUB_DOMAIN="mattermost"
fi
#echo "DEFAULT_SUB_DOMAIN:      ${DEFAULT_SUB_DOMAIN}"


## check if subdomain declared in pbase_repo.json needs to be updated
## handle case of new app running in a subdomain being overlaid on an existing apache running the root domain
## this is done by adding apache proxy

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


HAS_APACHE_CONF=""
HAS_APACHE_ROOTDOMAIN_CONF=""
HAS_APACHE_SUBDOMAIN_CONF=""

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

## check for case subdomain proxy to be added
ROOTDOMAIN_HTTP_CONF_FILE=""
SUBDOMAIN_HTTP_CONF_FILE=""


if [[ -e "/etc/httpd/conf.d/${THISDOMAINNAME}.conf" ]] ; then
  echo "Found existing Apache on this host, will configure Apache proxy"
  ROOTDOMAIN_HTTP_CONF_FILE="/etc/httpd/conf.d/${THISDOMAINNAME}.conf"
  HAS_APACHE_ROOTDOMAIN_CONF="true"
  HAS_APACHE_CONF="true"
fi

if [[ "${SUBDOMAIN_NAME}" == "" ]] ; then
  FULLDOMAINNAME="${THISDOMAINNAME}"
  echo "Using root domain:       ${FULLDOMAINNAME}"

  ## replace existing root domain conf
  if [[ -e "/etc/httpd/conf.d/${THISDOMAINNAME}.conf" ]] ; then
    echo "Found existing Apache root domain .conf file"
    SUBDOMAIN_HTTP_CONF_FILE="/etc/httpd/conf.d/${THISDOMAINNAME}.conf"
    HAS_APACHE_SUBDOMAIN_CONF=""
    HAS_APACHE_CONF="true"
  fi

else
  FULLDOMAINNAME="${SUBDOMAIN_NAME}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"

  ## replace existing subdomain conf
  if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" ]] ; then
    echo "Found existing Apache subdomain .conf file"
    ## mv "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf-DISABLED"
    SUBDOMAIN_HTTP_CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
    HAS_APACHE_SUBDOMAIN_CONF="true"
    HAS_APACHE_CONF="true"
  fi
fi


if [[ "${HAS_APACHE_CONF}" == "" ]] ; then
  echo "Found no existing Apache on this host"
else
  ## Check for /etc/httpd/conf.d/ssl.conf, comment it out if it exists
  commentOutFile "/etc/httpd/conf.d" "ssl.conf"
fi


DB_CONFIG_FILENAME="pbase_postgres.json"
MATTERMOST_CONFIG_FILENAME="pbase_mattermost.json"
echo "Mattermost config:       ${MODULE_CONFIG_DIR}/pbase_mattermost.json"

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_apache.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_lets_encrypt.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_mattermost.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_smtp.json  ${MODULE_CONFIG_DIR}/

if [[ -e "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}" ]] ; then
  echo "Setting aside previous preconfig file: ${DB_CONFIG_FILENAME}"
  DATE_SUFFIX="$(date +'%Y-%m-%d_%H-%M')"
  mv "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}-PREV-${DATE_SUFFIX}.json"
fi

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_postgres.json  ${MODULE_CONFIG_DIR}/

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
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_mattermost urlSubDomain
  setFieldInJsonModuleConfig ${DEFAULT_SUB_DOMAIN} pbase_apache urlSubDomain
  setFieldInJsonModuleConfig "false" pbase_apache enableCheckForWww
else
  echo "Setting empty urlSubDomain, Mattermost application will be root level of domain"
  echo "urlSubDomain:            ${DEFAULT_SUB_DOMAIN_QUOTED}"
  setFieldInJsonModuleConfig "" pbase_lets_encrypt urlSubDomain
  setFieldInJsonModuleConfig "" pbase_mattermost urlSubDomain
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
echo "RAND_PW_USER:            $RAND_PW_USER"

echo "Setting config with Postgres user and DB name for use by pbase-gitea"
echo "                         ${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

## provide random password in database config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"


echo ""
echo "Postgres, SMTP and Let's Encrypt module config files for Mattermost added."
echo "Next step - optional - review the configuration defaults provided"
echo "    under 'module-config.d' by editing their JSON text files. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_apache.json"
echo "  vi ${DB_CONFIG_FILENAME}"
echo "  vi pbase_lets_encrypt.json"
echo "  vi pbase_smtp.json"
echo "  vi pbase_mattermost.json"
echo ""

echo "Next step - install Postgres, Apache and Mattermost application with:"
echo ""
echo "  yum -y install pbase-postgres"
echo "  yum -y install pbase-mattermost"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_apache.json
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_lets_encrypt.json
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_mattermost.json
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_postgres.json
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_smtp.json