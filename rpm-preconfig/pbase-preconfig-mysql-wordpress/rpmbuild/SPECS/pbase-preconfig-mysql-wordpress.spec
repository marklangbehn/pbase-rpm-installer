Name: pbase-preconfig-mysql-wordpress
Version: 1.0
Release: 0
Summary: PBase MySQL preconfigure rpm, preset user and DB name for use by pbase-wordpress
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mysql-wordpress-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mysql-wordpress
Requires: pbase-php-transitive-dep, pbase-epel

%description
Configure MySQL preset user and DB name for use by pbase-wordpress

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


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo "PBase pre-configuration for MySQL and WordPress"
echo ""
echo "hostname:                $THISHOSTNAME"
echo "domainname:              $THISDOMAINNAME"


MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-mysql-wordpress/module-config-samples"
APACHE_CONFIG_FILENAME="pbase_apache.json"
DB_CONFIG_FILENAME="pbase_mysql.json"
WORDPRESS_CONFIG_FILENAME="pbase_wordpress.json"

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${APACHE_CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${DB_CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${WORDPRESS_CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/

## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"
echo "RAND_PW_ROOT:            $RAND_PW_ROOT"

echo "Setting config with MySQL user and DB name for use by pbase-wordpress"
echo "                         ${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

## provide random password in JSON config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"
sed -i "s/SHOmeddata/${RAND_PW_ROOT}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

echo ""
echo "MySQL module config file for Wordpress:"
echo "Next step - change the default MySQL DB root password and application-db"
echo "              config if needed by editing pbase_mysql.json"
echo "            change the Apache admin email if needed "
echo "              by editing pbase_apache.json"
echo "            change the Wordpress URI to be a string like 'wordpress' or 'blog'"
echo "              by editing the wordpressUriBase field in pbase_wordpress.json"
echo "              default is '' to configures Wordpress as the root-level website"
echo "            For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_mysql.json"
echo "  vi pbase_apache.json"
echo "  vi pbase_wordpress.json"
echo ""

echo "Next step - install Wordpress application stack with:"
echo ""
echo "  yum -y install pbase-wordpress-allinone"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-mysql-wordpress/module-config-samples/pbase_apache.json
/usr/local/pbase-data/pbase-preconfig-mysql-wordpress/module-config-samples/pbase_mysql.json
/usr/local/pbase-data/pbase-preconfig-mysql-wordpress/module-config-samples/pbase_wordpress.json
