Name: pbase-preconfig-postgres-mattermost
Version: 1.0
Release: 0
Summary: PBase Postgres preconfigure rpm, preset user and DB name for use by pbase-mattermost
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-postgres-mattermost-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-postgres-mattermost

%description
Configure Postgres preset user and DB name for use by pbase-mattermost

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


echo "PBase Postgres create config preset user and DB name for use by pbase-mattermost"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples"
DB_CONFIG_FILENAME="pbase_postgres.json"

mkdir -p ${MODULE_CONFIG_DIR}

echo "Mattermost config:       ${MODULE_CONFIG_DIR}/pbase_mattermost.json"
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_lets_encrypt.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_mattermost.json  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/pbase_postgres.json  ${MODULE_CONFIG_DIR}/


## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
echo "RAND_PW_USER:            $RAND_PW_USER"

## provide random password in JSON config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

echo ""
echo "Postgres module config file for Mattermost:"
echo "Next step - a) change the default Mattermost port, or select an "
echo "               Apache proxy for a subdomain or the base domain by "
echo "               editing pbase_mattermost.json"
echo "            b) change the default Postgres DB application-database, "
echo "               user, password and other config by "
echo "               pbase_postgres.json. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
## echo "  cp pbase_mattermost.json pbase_mattermost.json"
echo "  vi pbase_mattermost.json"
echo "  vi pbase_postgres.json"


echo "Next step - install postgres service with:"
echo "  yum install pbase-postgres"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_lets_encrypt.json
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_mattermost.json
/usr/local/pbase-data/pbase-preconfig-postgres-mattermost/module-config-samples/pbase_postgres.json
