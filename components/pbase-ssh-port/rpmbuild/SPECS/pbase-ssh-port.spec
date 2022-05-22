Name: pbase-ssh-port
Version: 1.0
Release: 2
Summary: PBase SSH port rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-ssh-port
Requires: jq

%description
Configures SSH custom port-number and whether to enable root login via ssh

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

check_linux_version() {
  AMAZON1_RELEASE=""
  AMAZON2_RELEASE=""
  AMAZON2022_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2 ')"
    AMAZON2022_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2022')"
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
  elif [[ "$AMAZON2022_RELEASE" != "" ]]; then
    echo "AMAZON2022_RELEASE:      $AMAZON2022_RELEASE"
    REDHAT_RELEASE_DIGIT="9"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}

echo "PBase SSH port"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## config is stored in json file with root-only permissions
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_ssh_port.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_ssh_port.json"
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


## look for config file "pbase_ssh_port.json"
PBASE_CONFIG_FILENAME="pbase_ssh_port.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "ENABLE_ROOT_LOGIN" ".pbase_ssh_port.enableRootLogin" "true"
parseConfig "SSH_PORT" ".pbase_ssh_port.port" "29900"

echo "ENABLE_ROOT_LOGIN:       $ENABLE_ROOT_LOGIN"
echo "SSH_PORT:                $SSH_PORT"
echo ""


## check which version of Linux is installed
check_linux_version

ENABLE_VALUE="no"
if [[ "$ENABLE_ROOT_LOGIN" == "true" ]] || [[ "$ENABLE_ROOT_LOGIN" == "yes" ]] || [[ "$ENABLE_ROOT_LOGIN" == "1" ]] ; then
  ENABLE_VALUE="yes"
fi

echo "Updating:                /etc/ssh/sshd_config"
echo "Setting PermitRootLogin: $ENABLE_VALUE"
echo "Setting Port:            $SSH_PORT"
echo ""

/bin/cp -f "/etc/ssh/sshd_config" "/etc/ssh/sshd_config-ORIG"

## Use Augeas tool to edit conf
cat <<EOF | augtool --noautoload
set /augeas/load/sshd_config
set /augeas/load/sshd_config/lens "Sshd.lns"
set /augeas/load/sshd_config/incl "/etc/ssh/sshd_config"
load
set /files/etc/ssh/sshd_config/PermitRootLogin "${ENABLE_VALUE}"
set /files/etc/ssh/sshd_config/Port "${SSH_PORT}"
save
EOF

echo "Restarting service:      sshd"

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/service sshd restart || fail "failed to restart sshd service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl restart sshd || fail "failed to restart sshd service"
fi

%files
