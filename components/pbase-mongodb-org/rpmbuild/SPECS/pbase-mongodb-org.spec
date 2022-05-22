Name: pbase-mongodb-org
Version: 1.0
Release: 2
Summary: PBase MongoDB Install
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-mongodb-org
Requires: mongodb-org,mongodb-org-server

%description
PBase MongoDB Install

%prep

%install

%clean

%pre

%post
##echo "rpm postinstall $1"

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

echo "PBase MongoDB service install"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi


## check which version of Linux is installed
check_linux_version

MONGO_CONF_FILE="/etc/mongodb.conf"

if [[ ! -e "$MONGO_CONF_FILE" ]]; then
  MONGO_CONF_FILE="/etc/mongod.conf"
fi

if [[ ! -e "$MONGO_CONF_FILE" ]]; then
  echo "Cannot find file:        $MONGO_CONF_FILE"
fi


## configure mongo bind_ip
LISTENADDR_ALL_LINE="bind_ip = 127.0.0.1"

## TODO fedora
LISTENADDR_ALLFEDORA="bindIp: 127.0.0.1,::1"
SEARCH_LISTENADDR_ALLFEDORA="^\s*bindIp: 127.0.0.1,::1"
SEARCH_LISTENADDR_ALLMONGO_ORG="^\s*bindIp: 127.0.0.1"

SEARCH_LISTENADDR_SET="^#${LISTENADDR_ALL_LINE}"
SEARCH_LISTENADDR_DFLT="bind_ip = 127.0.0.1"
REPLACE_LISTENER_LINE="${LISTENADDR_ALL_LINE}\n${SEARCH_LISTENADDR_DFLT}"


if [[ -e ${MONGO_CONF_FILE} ]]; then
  ALREADY_HAS_LISTENADDR=`grep "${SEARCH_LISTENADDR_ALLMONGO_ORG}" "${MONGO_CONF_FILE}"`
  if [[ "${ALREADY_HAS_LISTENADDR}" != "" ]]; then
    echo "ALREADY_HAS_LISTENADDR:  ${ALREADY_HAS_LISTENADDR}"
    echo "Already has correct bindIp line. Leaving unchanged."
  else
    ALREADY_HAS_LISTENADDR=`grep "${SEARCH_LISTENADDR_SET}" "${MONGO_CONF_FILE}"`
    echo "ALREADY_HAS_LISTENADDR:  ${ALREADY_HAS_LISTENADDR}"

    if [[ "${ALREADY_HAS_LISTENADDR}" == "" ]]; then
      ## make backup copy of file
      /bin/cp "${MONGO_CONF_FILE}" "${MONGO_CONF_FILE}-PREV"

      echo "Setting:                 ${LISTENADDR_ALL_LINE}"
      sed -i "s/${SEARCH_LISTENADDR_DFLT}/#${SEARCH_LISTENADDR_DFLT}/" "${MONGO_CONF_FILE}"
    else
      echo "Already has modified bind_ip line. Leaving unchanged."
    fi
  fi

else
  echo "not found: ${MONGO_CONF_FILE}"
fi

# Enable mongod service at boot-time, and start mongod service

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig mongod --level 345 on || fail "chkconfig failed to enable mongod service"
  /sbin/service mongod start || fail "failed to start mongod service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl enable mongod.service || fail "systemctl failed to enable mongod service"
  /bin/systemctl start mongod || fail "failed to start mongod service"
  /bin/systemctl status -l mongod
fi

## Add aliases helpful for admin tasks to .bashrc
append_bashrc_alias tailmongo "tail -f /var/log/mongodb/mongod.log"
append_bashrc_alias editmongoconf "/etc/mongodb.conf"

if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
  append_bashrc_alias stopmongo "service mongod stop"
  append_bashrc_alias startmongo "service mongod start"
  append_bashrc_alias statusmongo "service mongod status"
  append_bashrc_alias restartmongo "service mongod restart"
else
  append_bashrc_alias stopmongo "/bin/systemctl stop mongod"
  append_bashrc_alias startmongo "/bin/systemctl start mongod"
  append_bashrc_alias statusmongo "/bin/systemctl status mongod"
  append_bashrc_alias restartmongod "/bin/systemctl restart mongod"
fi

echo ""

echo "MongoDB service started, command line ready:"
echo "                         mongo"
echo ""

%files
