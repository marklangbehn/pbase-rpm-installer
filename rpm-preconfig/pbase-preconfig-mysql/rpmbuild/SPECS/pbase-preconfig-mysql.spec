Name: pbase-preconfig-mysql
Version: 1.0
Release: 1
Summary: PBase MySQL repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mysql-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mysql

%description
Configure yum repo for MySQL

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


echo "PBase MySQL create default module config"
echo ""

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-mysql/module-config-samples"
DB_CONFIG_FILENAME="pbase_mysql.json"

echo "MySQL config:            ${MODULE_CONFIG_DIR}/pbase_mysql.json"

if [[ -e "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}" ]] ; then
  echo "Setting aside previous preconfig file: ${DB_CONFIG_FILENAME}"
  DATE_SUFFIX="$(date +'%Y-%m-%d_%H-%M')"
  mv "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}-PREV-${DATE_SUFFIX}.json"
fi

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${DB_CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/

## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"
echo "RAND_PW_ROOT:            $RAND_PW_ROOT"

## provide random password in database config file
sed -i "s/shomeddata/${RAND_PW_USER}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"
sed -i "s/SHOmeddata/${RAND_PW_ROOT}/" "${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

echo ""
echo "MySQL module config file:"
echo "Next step - optional - change the default MySQL application-database name,"
echo "     user and password to be created by editing"
echo "     the sample config file. For example:"
echo ""

echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi ${DB_CONFIG_FILENAME}""

echo ""
echo "Next step - install MySQL with:"
echo ""
echo "  yum -y install pbase-mysql"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-mysql/module-config-samples/pbase_mysql.json
