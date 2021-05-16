Name: pbase-ssh-fail2ban
Version: 1.0
Release: 1
Summary: PBase SSH fail2ban rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-ssh-fail2ban-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-ssh-fail2ban
Requires: jq, fail2ban, firewalld

%description
Configures SSH fail2ban security service

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

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


echo "PBase SSH fail2ban"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## config is stored in json file with root-only permissions
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_ssh_fail2ban.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_ssh_fail2ban.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.js"
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


## look for config file "pbase_ssh_fail2ban.json"
PBASE_CONFIG_FILENAME="pbase_ssh_fail2ban.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "FAIL2BAN_ENABLE" ".pbase_ssh_fail2ban.enable" "true"
parseConfig "IGNORE_IP" ".pbase_ssh_fail2ban.ignoreip" "[]"

echo "FAIL2BAN_ENABLE:         $FAIL2BAN_ENABLE"
echo "IGNORE_IP:               $IGNORE_IP"
echo ""


## check which version of Linux is installed
check_linux_version

#ENABLE_VALUE="no"
#if [[ "$ENABLE_ROOT_LOGIN" == "true" ]] || [[ "$ENABLE_ROOT_LOGIN" == "yes" ]] || [[ "$ENABLE_ROOT_LOGIN" == "1" ]] ; then
#  ENABLE_VALUE="yes"
#fi

echo "Installing default configuration"
echo "                         /etc-fail2ban/jail.local"
echo "                         /etc-fail2ban/jail.d/jail.local"

/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-ssh-fail2ban/etc-fail2ban/jail.local  /etc/fail2ban/
/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-ssh-fail2ban/etc-fail2ban-jail.d/sshd.conf  /etc/fail2ban/jail.d/

echo "Restarting service:      fail2ban"

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/service fail2ban restart || fail "failed to restart fail2ban service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl enable fail2ban
  /bin/systemctl restart fail2ban || fail "failed to restart fail2ban service"
fi


## helpful aliases

append_bashrc_alias tailfail2ban "tail -n40 -f /var/log/fail2ban.log"
append_bashrc_alias editfail2banlocal "vi /etc/fail2ban/jail.local"
append_bashrc_alias editfail2bansshd "vi /etc/fail2ban/jail.d/sshd.conf"
append_bashrc_alias statusfail2ban "fail2ban-client status sshd"
append_bashrc_alias statusfail2bansshd "fail2ban-client status sshd"
append_bashrc_alias unbanfail2ban "function _unbanfail2ban(){ fail2ban-client set sshd unbanip \$1;  };_unbanfail2ban"

## alias unbanfail2ban='function _unbanfail2ban(){ fail2ban-client set sshd unbanip $1;  };_unbanfail2ban'

echo "How to check for which IPs are banned and how to unban their address:"
echo "Option 1 - using the fail2ban-client (for example 192.168.2.x)"
echo "  fail2ban-client status sshd"
echo "  fail2ban-client set sshd unbanip 192.168.2.x"
echo ""
echo "Option 2 - using the shell aliases"
echo "  statusfail2ban"
echo "  unbanfail2ban 192.168.2.x"


%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-ssh-fail2ban/etc-fail2ban/jail.local
/usr/local/pbase-data/pbase-ssh-fail2ban/etc-fail2ban-jail.d/sshd.conf
