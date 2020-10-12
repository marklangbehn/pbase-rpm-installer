Name: pbase-preconfig-mysql-mattermost
Version: 1.0
Release: 0
Summary: PBase MySQL preconfigure rpm, preset user and DB name for use by pbase-mattermost
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mysql-mattermost-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mysql-mattermost
Requires: pbase-epel

%description
Configure MySQL preset user and DB name for use by pbase-mattermost

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


echo "PBase MySQL create config preset user and DB name for use by pbase-mattermost"

check_linux_version


MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/module-config-samples"
DB_CONFIG_FILENAME="pbase_mysql80community.json"

mkdir -p ${MODULE_CONFIG_DIR}

if [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]]; then
  DB_CONFIG_FILENAME="pbase_mysql80community.json"
  echo "MySQL 8.0 config:        ${MODULE_CONFIG_DIR}/pbase_mysql80community.json"
  /bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_mysql80community.json  ${MODULE_CONFIG_DIR}/pbase_mysql80community.json
else
  DB_CONFIG_FILENAME="pbase_mysql.json"
  echo "MySQL config:            ${MODULE_CONFIG_DIR}/pbase_mysql.json"
  /bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_mysql.json  ${MODULE_CONFIG_DIR}/pbase_mysql.json
fi

echo "Mattermost config:       ${MODULE_CONFIG_DIR}/pbase_mattermost.json"
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_apache.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_lets_encrypt.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_mattermost.json  ${MODULE_CONFIG_DIR}/


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"
echo "RAND_PW_ROOT:            $RAND_PW_ROOT"

## provide random password in JSON config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"
sed -i "s/SHOmeddata/${RAND_PW_ROOT}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"


echo ""
echo "MySQL module config file for Mattermost:"
echo "Next step - a) change the default Mattermost port, or select an Apache proxy"
echo "               for a subdomain or the base domain in pbase_mattermost.json"
echo "            b) change the default MySQL DB root password and application-db"
echo "                and user and other config in pbase_mysql.json. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
## echo "  cp pbase_mattermost.json-SAMPLE pbase_mattermost.json"  ##MySQL config
echo "  vi pbase_mattermost.json"
echo "  vi ${DB_CONFIG_FILENAME}"

echo ""


echo "Next step - install mysql service with:"
echo "  yum -y install pbase-mysql"
echo "  yum -y install pbase-mattermost"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/etc-pki-rpm-gpg/RPM-GPG-KEY-mysql
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/etc-yum-repos-d/el6/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/etc-yum-repos-d/el7/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/etc-yum-repos-d/fedora/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/module-config-samples/pbase_apache.json
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/module-config-samples/pbase_lets_encrypt.json
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/module-config-samples/pbase_mattermost.json
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/module-config-samples/pbase_mysql.json
/usr/local/pbase-data/pbase-preconfig-mysql-mattermost/module-config-samples/pbase_mysql80community.json
