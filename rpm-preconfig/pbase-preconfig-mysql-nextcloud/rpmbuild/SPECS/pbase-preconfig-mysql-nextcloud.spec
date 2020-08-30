Name: pbase-preconfig-mysql-nextcloud
Version: 1.0
Release: 0
Summary: PBase MySQL preconfigure rpm, preset user and DB name for use by pbase-nextcloud
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mysql-nextcloud-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mysql-nextcloud
Requires: pbase-php-transitive-dep, pbase-preconfig-mysql80community


%description
Configure MySQL preset user and DB name for use by pbase-nextcloud

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


## echo "PBase MySQL create config preset user and DB name for use by pbase-nextcloud"
echo "PBase MySQL 8.0 community create config preset user and DB name for use by pbase-nextcloud"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples"
DB_CONFIG_FILENAME="pbase_mysql80community.json"

echo "MySQL 8.0 config:        ${MODULE_CONFIG_DIR}/pbase_mysql80community.json"
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_mysql80community.json  ${MODULE_CONFIG_DIR}/pbase_mysql80community.json

## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"
echo "RAND_PW_ROOT:            $RAND_PW_ROOT"

## provide random password in JSON config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"
sed -i "s/SHOmeddata/${RAND_PW_ROOT}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

echo ""
echo "MySQL module config file for Nextcloud:"
echo "Next step - change the default MySQL DB root password and application-db"
## echo "            config by editing pbase_mysql.json. For example:"
echo "            config by editing ${DB_CONFIG_FILENAME}. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi ${DB_CONFIG_FILENAME}"
echo ""

echo "Next step - install mysqld service with:"
echo ""
## echo "  yum -y install pbase-mysql"
echo "  yum -y install pbase-mysql80community"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/admin-only/module-config.d/
/usr/local/pbase-data/pbase-preconfig-mysql-nextcloud/module-config-samples/pbase_mysql80community.json