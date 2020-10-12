Name: pbase-timesync-enable
Version: 1.0
Release: 0
Summary: PBase NTP/Chrony service enable
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-timesync-enable
Requires: pbase-timesync-enable-transitive-dep, jq

%description
PBase NTP/Chrony service enable

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


echo "PBase NTP/Chrony time-sync enable"

## config is stored in json file with root-only permissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_timesync_enable.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_timesync_enable.json"
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


## look for either separate config file "pbase_timesync_enable.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_timesync_enable.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "CONFIG_TIMEZONE" ".pbase_timesync_enable.timeZone" "UTC"

echo "CONFIG_TIMEZONE:         $CONFIG_TIMEZONE"


## check which version of Linux is installed
check_linux_version

## set timezone, default is UTC
if [[ -e "/etc/localtime.RPMSAVE" ]]; then
  /bin/rm -f /etc/localtime.RPMSAVE
fi

echo "Executing:       ln -s /usr/share/zoneinfo/${CONFIG_TIMEZONE} /etc/localtime"

mv /etc/localtime /etc/localtime.RPMSAVE
ln -s /usr/share/zoneinfo/${CONFIG_TIMEZONE} /etc/localtime


## Add aliases helpful for admin tasks to .bashrc

if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
  append_bashrc_alias editntpconf "vi /etc/ntp.conf"
  append_bashrc_alias stopntpd "service ntpd stop"
  append_bashrc_alias startntpd "service ntpd start"
  append_bashrc_alias statusntpd "service ntpd status"
  append_bashrc_alias restartntpd "service ntpd restart"
else
  append_bashrc_alias editchronyconf "vi /etc/chrony.conf"
  append_bashrc_alias stopchronyd "/bin/systemctl stop chronyd"
  append_bashrc_alias startchronyd "/bin/systemctl start chronyd"
  append_bashrc_alias statuschronyd "/bin/systemctl status chronyd"
  append_bashrc_alias restartchronyd "/bin/systemctl restart chronyd"

  append_bashrc_alias chronysources "chronyc sources -v"
fi


if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  echo "Enabling time-sync:      ntpd"
  /sbin/chkconfig ntpd --level 345 on || fail "chkconfig failed to enable ntpd service"
  /sbin/service ntpd restart
else
  echo "Enabling time-sync:      chronyd"
  systemctl daemon-reload
  systemctl enable chronyd
  systemctl restart chronyd

  ## show ntp servers contacted
  sleep 10
  chronyc sources -v
fi


echo "Synced to ${CONFIG_TIMEZONE} Timezone"
##echo ""

%files
