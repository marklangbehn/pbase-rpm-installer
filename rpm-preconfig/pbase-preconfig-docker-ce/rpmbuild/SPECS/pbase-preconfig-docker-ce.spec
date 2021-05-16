Name: pbase-preconfig-docker-ce
Version: 1.0
Release: 1
Summary: PBase Docker CE repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-docker-ce-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-docker-ce
Requires: yum-utils,device-mapper-persistent-data,lvm2,pbase-preconfig-docker-ce-transitive-dep, jq

%description
Configure yum repo and dependencies for current Docker CE version

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
## config is stored in json file with root-only permissions
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.json"
  PBASE_CONFIG_DIR="${PBASE_CONFIG_BASE}/module-config.d"

  ## Look for config .json file in one of two places.
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
  MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d/"
  SAMPLE_SOURCE_DIR="/usr/local/pbase-data/pbase-preconfig-docker-ce/module-config-samples/"

  SOURCE_DIR="$4"
  if [[ "$SOURCE_DIR" == "" ]]; then
    SOURCE_DIR="$MODULE_CONFIG_DIR"
  fi

  CONFIG_FILE_NAME="${MODULE}.json"
  TEMPLATE_JSON_FILE="${SOURCE_DIR}${CONFIG_FILE_NAME}"
  /bin/cp -f "${TEMPLATE_JSON_FILE}" "/tmp/${CONFIG_FILE_NAME}"

  ## set a value in the json file
  PREFIX="jq '.${MODULE}.${FULLFIELDNAME}= \""
  SUFFIX="\"'"
  JQ_COMMAND="${PREFIX}${NEWVALUE}${SUFFIX} /tmp/${CONFIG_FILE_NAME} > ${MODULE_CONFIG_DIR}${CONFIG_FILE_NAME}"

  ##echo "Executing:  eval $JQ_COMMAND"
  eval $JQ_COMMAND

  /bin/rm -f "/tmp/${CONFIG_FILE_NAME}"
}


echo "PBase Docker CE yum repos and dependencies pre-configuration"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

echo ""
MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for config file like "pbase_repo.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_DESKTOP_USER_NAME" ".pbase_repo.defaultDesktopUsername" ""
DESKTOP_USER_NAME=""

if [[ "$DEFAULT_DESKTOP_USER_NAME" != "" ]] && [[ "$DEFAULT_DESKTOP_USER_NAME" != null ]]; then
  echo "defaultDesktopUsername:  $DEFAULT_DESKTOP_USER_NAME"
  DESKTOP_USER_NAME="$DEFAULT_DESKTOP_USER_NAME"
else
  echo "defaultDesktopUsername:  $DEFAULT_DESKTOP_USER_NAME"
  DESKTOP_USER_NAME=""
fi

## check which version of Linux is installed
check_linux_version

## default repo for EL7
YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-yum-repos-d/el8/docker-ce.repo"

/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-docker-ce/etc-pki-rpm-gpg/docker-ce-gpg  /etc/pki/rpm-gpg

if [[ -e "/etc/yum.repos.d/docker-ce.repo" ]] ; then
  echo "Existing YUM repo:       /etc/yum.repos.d/docker-ce.repo"
else
  if [[ "$FEDORA_RELEASE" != "" ]] ; then
    echo "docker-ce for Fedora"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-yum-repos-d/fedora/docker-ce.repo"
  elif [[ "$REDHAT_RELEASE_DIGIT" == "6" ]] ; then
    echo "docker-ce for EL6 not available"
    return 1
  elif [[ "$REDHAT_RELEASE_DIGIT" == "7" ]] ; then
    echo "docker-ce for EL7"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-yum-repos-d/el7/docker-ce.repo"
  elif [[ "$REDHAT_RELEASE_DIGIT" == "8" ]] ; then
    echo "docker-ce for EL8"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-yum-repos-d/el8/docker-ce.repo"
  fi

  echo "docker-ce.repo:          /etc/yum.repos.d/docker-ce.repo"
  /bin/cp -f $YUM_REPO_PATH /etc/yum.repos.d/
fi


## check if desktop username was specified
if [[ "$DESKTOP_USER_NAME" != "" ]] ; then
  echo "Docker username:         $DESKTOP_USER_NAME"
  setFieldInJsonModuleConfig $DESKTOP_USER_NAME pbase_docker_ce addUserToDockerGroup "/usr/local/pbase-data/pbase-preconfig-docker-ce/module-config-samples/"
else
  echo ""
  echo "Next step - Enable adding a user to the docker group by making "
  echo "     a copy of the config sample file and editing it. For example:"
  echo ""
  echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
  echo "  cp /usr/local/pbase-data/pbase-preconfig-docker-ce/module-config-samples/pbase_docker_ce.json ."
  echo "  vi pbase_docker_ce.json"
fi

echo ""
echo "Next step - install Docker CE with:"
echo "  yum -y install pbase-docker-ce"
echo ""

%preun
echo "rpm preuninstall"

## remove the repo file added by script
/bin/rm -f /etc/yum.repos.d/docker-ce.repo


%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-yum-repos-d/el7/docker-ce.repo
/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-yum-repos-d/el8/docker-ce.repo
/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-yum-repos-d/fedora/docker-ce.repo
/usr/local/pbase-data/pbase-preconfig-docker-ce/etc-pki-rpm-gpg/docker-ce-gpg
/usr/local/pbase-data/pbase-preconfig-docker-ce/module-config-samples/pbase_docker_ce.json
