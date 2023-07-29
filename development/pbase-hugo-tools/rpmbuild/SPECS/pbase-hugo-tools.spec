Name: pbase-hugo-tools
Version: 1.0
Release: 0
Summary: PBase Hugo download rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-hugo-tools
Requires: curl, jq, pbase-golang-tools

%description
PBase Hugo executable download

%prep

%install

%clean

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


echo "PBase Hugo executable download"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## config is stored in json file with root-only permissions
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
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

## check_linux_version

## look for config file "pbase_hugo_tools.json"
PBASE_CONFIG_FILENAME="pbase_hugo_tools.json"
#locateConfigFile "$PBASE_CONFIG_FILENAME"
##TODO customize the release filename: hugo_extended_${HUGO_VERS}_linux-amd64.tar.gz
## fetch config value from JSON file
## version to download
#parseConfig "VERSION_CONFIG" ".pbase_hugo_tools.hugoVersion" "0.110.0"
#echo "VERSION_CONFIG:          $VERSION_CONFIG"
#HUGO_VERS="$VERSION_CONFIG"

HUGO_VERS="0.110.0"


## check if already installed
if [[ -e "/usr/local/bin/hugo" ]]; then
  echo "Hugo executable /usr/local/bin/hugo already exists - exiting"
  exit 0
fi

mkdir -p /usr/local/pbase-data/pbase-hugo-tools
cd /usr/local/pbase-data/pbase-hugo-tools
/bin/rm -f *.zip

## determine latest release
HUGO_VERS="$(curl https://api.github.com/repos/gohugoio/hugo/releases/latest 2>/dev/null | jq -r '.name | ltrimstr("v")')"
echo "HUGO_VERS:               ${HUGO_VERS}"

HUGO_EXECUTABLE="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERS}/hugo_extended_${HUGO_VERS}_linux-amd64.tar.gz"

echo "Downloading Hugo binary: $HUGO_EXECUTABLE"
curl -sLO "$HUGO_EXECUTABLE"

ls -l *.gz

gunzip hugo*.gz
tar xf hugo*.tar -C /usr/local/bin/
/bin/rm -f tar xf hugo*.tar

echo ""
echo "Hugo executable ready:"
chmod +x /usr/local/bin/hugo
ls -l /usr/local/bin/hugo

## show the hugo version
/usr/local/bin/hugo version

## show the go version
go version

echo ""

%files
