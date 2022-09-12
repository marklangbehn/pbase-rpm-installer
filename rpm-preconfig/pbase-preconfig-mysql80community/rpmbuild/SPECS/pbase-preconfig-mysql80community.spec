Name: pbase-preconfig-mysql80community
Version: 1.0
Release: 2
Summary: PBase MySQL 8.0 repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mysql80community-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mysql80community

%description
Configure yum repo for MySQL 8.0 Community version

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

echo "PBase MySQL 8.0 Community repo and default module config"
echo ""

## check which version of Linux is installed
check_linux_version

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-mysql80community/module-config-samples"
DB_CONFIG_FILENAME="pbase_mysql80community.json"

echo "MySQL config:            ${MODULE_CONFIG_DIR}/${DB_CONFIG_FILENAME}"

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

## GPG key
/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-mysql80community/etc-pki-rpm-gpg/RPM-GPG-KEY-mysql /etc/pki/rpm-gpg

if [[ -e "/etc/yum.repos.d/mysql-community.repo" ]] ; then
    echo "Existing mysql-community.repo found, leaving unchanged"
elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]] ; then
    echo "MySQL 8.0 el6:           /etc/yum.repos.d/mysql-community.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el6/mysql-community.repo /etc/yum.repos.d/mysql-community.repo
elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]] ; then
    echo "MySQL 8.0 el7:           /etc/yum.repos.d/mysql-community.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el7/mysql-community.repo /etc/yum.repos.d/mysql-community.repo
elif [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]] ; then
    echo "MySQL 8.0 el8:           /etc/yum.repos.d/mysql-community.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el8/mysql-community.repo /etc/yum.repos.d/mysql-community.repo
elif [[ "${REDHAT_RELEASE_DIGIT}" == "9" ]] ; then
    echo "MySQL 8.0 el9:           /etc/yum.repos.d/mysql-community.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el9/mysql-community.repo /etc/yum.repos.d/mysql-community.repo
elif [[ "${FEDORA_RELEASE}" != "" ]] ; then
    echo "MySQL 8.0 fedora:        /etc/yum.repos.d/mysql-community.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/fedora/mysql-community.repo /etc/yum.repos.d/mysql-community.repo
else
    echo "Leaving unchanged"
fi


echo ""
echo "MySQL 8.0 community repo configured."
echo "Next step - optional - change the default MySQL application-database name,"
echo "     user and password to be created by editing"
echo "     the sample config file. For example:"
echo ""

echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi ${DB_CONFIG_FILENAME}""

echo ""
echo "Next step - install MySQL with:"
echo ""
echo "  yum -y install pbase-mysql80community"
echo ""


%preun
echo "rpm preuninstall"

## remove the repo file added by script
/bin/rm -f /etc/yum.repos.d/mysql-community.repo

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el6/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el7/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el8/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/el9/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/fedora/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-pki-rpm-gpg/RPM-GPG-KEY-mysql
/usr/local/pbase-data/pbase-preconfig-mysql80community/module-config-samples/pbase_mysql80community.json
