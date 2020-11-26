Name: pbase-preconfig-postgres-mastodon
Version: 1.0
Release: 0
Summary: PBase Postgres preconfigure rpm, preset user and DB name for use by pbase-mastodon
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-postgres-mastodon-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-postgres-mastodon
Requires: pbase-preconfig-yarn, pbase-epel, jq

%description
Configure Postgres preset user and DB name for use by pbase-mastodon

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
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_apache.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.json"
  PBASE_CONFIG_DIR="${PBASE_CONFIG_BASE}/module-config.d"

  ## Look for config .json file in one of two places.
  ##     /usr/local/pbase-data/admin-only/pbase_module_config.json
  ## or
  ##     /usr/local/pbase-data/admin-only/module-config.d/pbase_apache.json

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


echo "PBase Postgres create config preset user and DB name for use by pbase-mastodon"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-postgres-mastodon/module-config-samples"

PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for either separate config file like "pbase_repo.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_EMAIL_ADDRESS" ".pbase_repo.defaultEmailAddress" ""

DB_CONFIG_FILENAME="pbase_postgres.json"


echo "Mastodon config:         ${MODULE_CONFIG_DIR}/activpb_mastodon.json"
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_lets_encrypt.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/activpb_mastodon.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_postgres.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_smtp.json  ${MODULE_CONFIG_DIR}/


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
echo "RAND_PW_USER:            $RAND_PW_USER"

## provide random password in database config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

## provide domainname in smtp config file
sed -i "s/example.com/${THISDOMAINNAME}/" "${MODULE_CONFIG_DIR}/pbase_smtp.json"

## when defined in pbase_repo.json use that to provide the Let's Encrypt email address
if [[ $DEFAULT_EMAIL_ADDRESS != "" ]]; then
  echo "Setting 'defaultEmailAddress' in pbase_apache.json and pbase_lets_encrypt.json"
  echo "                         ${DEFAULT_EMAIL_ADDRESS}"
  sed -i "s/yoursysadmin@yourrealmail.com/${DEFAULT_EMAIL_ADDRESS}/" "${MODULE_CONFIG_DIR}/pbase_lets_encrypt.json"
  sed -i "s/yoursysadmin@yourrealmail.com/${DEFAULT_EMAIL_ADDRESS}/" "${MODULE_CONFIG_DIR}/pbase_apache.json"
fi


echo ""
echo "Postgres, SMTP and Let's Encrypt module config files for Mastodon added."
echo "Next step - required - customize your configuration by editing these JSON files:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_lets_encrypt.json"
echo "  vi activpb_mastodon.json"
echo "  vi pbase_postgres.json"
echo "  vi pbase_smtp.json"
echo ""

echo "Next step - optional install local postgres service with:"
echo "  yum -y install pbase-postgres"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-postgres-mastodon/module-config-samples/activpb_mastodon.json
/usr/local/pbase-data/pbase-preconfig-postgres-mastodon/module-config-samples/pbase_lets_encrypt.json
/usr/local/pbase-data/pbase-preconfig-postgres-mastodon/module-config-samples/pbase_postgres.json
/usr/local/pbase-data/pbase-preconfig-postgres-mastodon/module-config-samples/pbase_s3storage.json
/usr/local/pbase-data/pbase-preconfig-postgres-mastodon/module-config-samples/pbase_smtp.json
