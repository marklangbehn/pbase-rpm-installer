Name: pbase-preconfig-mysql80community
Version: 1.0
Release: 0
Summary: PBase MySQL 8.0 repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mysql80community-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mysql80community

%description
Configure yum repo for current MySQL 8.0 version

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



echo "PBase MySQL 8.0 repo pre-configuration"

## check which version of Linux is installed
check_linux_version

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
elif [[ "${FEDORA_RELEASE}" != "" ]] ; then
    echo "MySQL 8.0 fedora:        /etc/yum.repos.d/mysql-community.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/fedora/mysql-community.repo /etc/yum.repos.d/mysql-community.repo
else
    echo "Leaving unchanged"
fi


echo ""
echo "MySQL 8.0 community repo configured."

echo "Next step - optional - change the default MySQL DB root password and"
echo "    application-db and user and other default config by making a copy"
echo "    of the sample file and editing it. For example:"
echo ""

echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp ../module-config-samples/pbase_mysql80community.json ."
echo "  vi pbase_mysql80community.json"

echo ""
echo "Next step - install mysqld service with:"
echo ""
echo "  yum -y install mysql-community-server"
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
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-yum-repos-d/fedora/mysql-community.repo
/usr/local/pbase-data/pbase-preconfig-mysql80community/etc-pki-rpm-gpg/RPM-GPG-KEY-mysql
/usr/local/pbase-data/admin-only/module-config-samples/pbase_mysql80community.json
