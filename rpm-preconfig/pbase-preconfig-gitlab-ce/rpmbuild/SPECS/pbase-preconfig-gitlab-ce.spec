Name: pbase-preconfig-gitlab-ce
Version: 1.0
Release: 0
Summary: PBase GitLab CE repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-gitlab-ce-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-gitlab-ce
Requires: curl, policycoreutils, openssh-server, python3-policycoreutils, jq

%description
Configure yum repo and dependencies for GitLab CE

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


echo "PBase GitLab CE yum repos and dependencies pre-configuration"
echo ""

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-postgres-gitea/module-config-samples"

PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for either separate config file like "pbase_repo.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_EMAIL_ADDRESS" ".pbase_repo.defaultEmailAddress" ""

GITLAB_CONFIG_FILENAME="pbase_gitlab_ce.json"
echo "Gitea config:            ${MODULE_CONFIG_DIR}/${GITLAB_CONFIG_FILENAME}"

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${GITLAB_CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_smtp.json  ${MODULE_CONFIG_DIR}/

## check which version of Linux is installed
check_linux_version

## default repo path
YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el8/gitlab_gitlab-ce.repo"

## /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-pki-rpm-gpg/gitlab-ce-gpg  /etc/pki/rpm-gpg

if [[ -e "/etc/yum.repos.d/gitlab_gitlab-ce.repo" ]] ; then
  echo "Existing YUM repo:       /etc/yum.repos.d/gitlab_gitlab-ce.repo"
else
  if [[ "$FEDORA_RELEASE" != "" ]] ; then
    echo "gitlab-ce for Fedora"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/fedora/gitlab_gitlab-ce.repo"
  elif [[ "$REDHAT_RELEASE_DIGIT" == "6" ]] ; then
    echo "gitlab-ce for EL6 not available"
    return 1
  elif [[ "$REDHAT_RELEASE_DIGIT" == "7" ]] ; then
    echo "gitlab-ce for EL7"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el7/gitlab_gitlab-ce.repo"
  elif [[ "$REDHAT_RELEASE_DIGIT" == "8" ]] ; then
    echo "gitlab-ce for EL8"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el8/gitlab_gitlab-ce.repo"
  fi

  echo "gitlab_gitlab-ce.repo:   /etc/yum.repos.d/gitlab_gitlab-ce.repo"
  /bin/cp -f $YUM_REPO_PATH /etc/yum.repos.d/
fi

## when defined in pbase_repo.json use that to provide the Let's Encrypt email address
if [[ $DEFAULT_EMAIL_ADDRESS != "" ]]; then
  echo "Setting 'defaultEmailAddress' in pbase_gitlab_ce.json"
  echo "                         ${DEFAULT_EMAIL_ADDRESS}"
  sed -i "s/yoursysadmin@yourrealmail.com/${DEFAULT_EMAIL_ADDRESS}/" "${MODULE_CONFIG_DIR}/pbase_gitlab_ce.json"
fi


echo ""
echo "GitLab CE repo configured."
echo "Next step - optional - change the default GitLab setup by editing"
echo "    pbase_gitlab_ce.json. For example:"
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_gitlab_ce.json"

echo ""
echo "Next step - install GitLab CE with:"
echo "  yum -y install pbase-gitlab-ce"
echo ""

%preun
echo "rpm preuninstall"

## remove the repo file added by script
/bin/rm -f /etc/yum.repos.d/gitlab_gitlab-ce.repo


%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el7/gitlab_gitlab-ce.repo
/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el8/gitlab_gitlab-ce.repo
/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/fedora/gitlab_gitlab-ce.repo
/usr/local/pbase-data/pbase-preconfig-postgres-gitea/module-config-samples/pbase_gitlab_ce.json
/usr/local/pbase-data/pbase-preconfig-postgres-gitea/module-config-samples/pbase_smtp.json
