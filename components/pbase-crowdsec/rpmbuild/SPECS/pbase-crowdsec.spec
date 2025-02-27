Name: pbase-crowdsec
Version: 1.0
Release: 1
Summary: PBase Crowdsec Install
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-crowdsec
Requires: gettext, newt, curl, wget

%description
PBase Crowdsec Install

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

echo "PBase Crowdsec Install"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## config may be stored in json file with root-only permissions
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

## look for config file "pbase_crowdsec.json"
PBASE_CONFIG_FILENAME="pbase_crowdsec.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "CROWDSEC_VERSION" ".pbase_crowdsec.crowdsecVersion" ""
parseConfig "UNATTENDED_INSTALL" ".pbase_crowdsec.unattendedInstall" "false"


echo "Downloading binary:      crowdsec-release.tgz"
cd /opt
curl -s https://api.github.com/repos/crowdsecurity/crowdsec/releases/latest | grep browser_download_url| cut -d '"' -f 4  | wget -q -i -
tar xzf crowdsec-release.tgz
/bin/rm -f crowdsec-release.tgz

echo "Done"
ls -l

if [[ "${UNATTENDED_INSTALL}" == "true"  ]] ; then
  echo "Executing Crowdsec unattended setup..."
  echo "  cd /opt/crowdsec*"
  echo "  ./wizard.sh --unattended"
  echo ""

  cd /opt/crowdsec*
  ./wizard.sh --unattended
else
  echo "Next step - required - execute these manual Crowdsec setup commands."
  echo "  cd /opt/crowdsec*"
  echo "  ./wizard.sh --install"
  echo ""
fi

echo ""
echo "Enabling crowdsec service"
/bin/systemctl daemon-reload
/bin/systemctl enable crowdsec

if [[ "${UNATTENDED_INSTALL}" == "true"  ]] ; then
  echo "Starting crowdsec service"
  /bin/systemctl start crowdsec
else
  echo "After completing crowdsec setup it must be started with 'systemctl start crowdsec'"
fi

/bin/systemctl status crowdsec

## Add aliases helpful for admin tasks to .bashrc
echo "" >> /root/.bashrc

CROWDSEC_LOG_FILE="/var/log/crowdsec.log"
CROWDSEC_CONF_FILE="/etc/crowdsec/config/default.yaml"

append_bashrc_alias tailcrowdsec "tail -n40 -f $CROWDSEC_LOG_FILE"
append_bashrc_alias editcrowdsecconf "vi $CROWDSEC_CONF_FILE"

append_bashrc_alias stopcrowdsec "/bin/systemctl stop crowdsec"
append_bashrc_alias startcrowdsec "/bin/systemctl start crowdsec"
append_bashrc_alias statuscrowdsec "/bin/systemctl status crowdsec"
append_bashrc_alias restartcrowdsec "/bin/systemctl restart crowdsec"

%files
