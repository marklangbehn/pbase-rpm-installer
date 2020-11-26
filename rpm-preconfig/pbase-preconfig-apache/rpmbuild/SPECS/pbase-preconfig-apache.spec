Name: pbase-preconfig-apache
Version: 1.0
Release: 0
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
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase Apache httpd pre-config file create"

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


MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-apache/module-config-samples"

PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for either separate config file like "pbase_repo.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_EMAIL_ADDRESS" ".pbase_repo.defaultEmailAddress" ""

## when email is defined in pbase_repo.json use that to provide the Apache httpd.conf email address
if [[ $DEFAULT_EMAIL_ADDRESS != "" ]]; then
  echo "Setting 'defaultEmailAddress' in pbase_apache.json"
  echo "                         ${DEFAULT_EMAIL_ADDRESS}"
  /bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_apache.json  ${MODULE_CONFIG_DIR}/
  sed -i "s/yoursysadmin@yourrealmail.com/${DEFAULT_EMAIL_ADDRESS}/" "${MODULE_CONFIG_DIR}/pbase_apache.json"

  echo ""
  echo "Next step - optional - change the Apache server default config by"
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