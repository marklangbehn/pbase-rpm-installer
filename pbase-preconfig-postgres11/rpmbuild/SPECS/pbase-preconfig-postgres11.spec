Name: pbase-preconfig-postgres11
Version: 1.0
Release: 0
Summary: PBase PostgreSQL 11 repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-postgres11-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-postgres11
Requires: jq

%description
Configure yum repo for PostgreSQL 11/12
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


echo "PBase Postgres 11/12 repo pre-configuration"
echo ""

## check which version of Linux is installed
check_linux_version

/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-postgres11/etc-pki-rpm-gpg/RPM-GPG-KEY-PGDG /etc/pki/rpm-gpg

if [[ "$FEDORA_RELEASE" != "" ]] ; then
    if [[ -f "/etc/yum.repos.d/pgdg-fedora-all.repo" ]]; then
      echo "Existing Postgres pgdg-fedora-all.repo found, leaving unchanged"
    else
      echo "Postgres for Fedora:        /etc/yum.repos.d/pgdg-fedora-all.repo"
      /bin/cp -f /usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/fedora/pgdg-fedora-all.repo /etc/yum.repos.d/
    fi
elif [[ "$AMAZON1_RELEASE" != "" ]] || [[ "$AMAZON2_RELEASE" != "" ]] ; then
    if [[ -f "/etc/yum.repos.d/pgdg-redhat-all.repo" ]]; then
      echo "Existing Postgres repo found, leaving unchanged"
    else
      echo "Postgres for AWS:        /etc/yum.repos.d/pgdg-redhat-amzn2.repo"
      /bin/cp -f /usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/pgdg-redhat-amzn2.repo /etc/yum.repos.d/pgdg-redhat-amzn2.repo
    fi
else
  if [[ -f "/etc/yum.repos.d/pgdg-redhat-all.repo" ]]; then
    echo "Existing Postgres repo found, leaving unchanged"
  elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
    echo "Postgres for EL6:        /etc/yum.repos.d/pgdg-redhat-all.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/pgdg-redhat-all.repo /etc/yum.repos.d/pgdg-redhat-all.repo
  elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]]; then
    echo "Postgres for EL7:        /etc/yum.repos.d/pgdg-redhat-all.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/pgdg-redhat-all.repo /etc/yum.repos.d/pgdg-redhat-all.repo
  else
    echo "Postgres for EL8:        /etc/yum.repos.d/pgdg-redhat-all.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/pgdg-redhat-all.repo /etc/yum.repos.d/pgdg-redhat-all.repo
  fi
fi


echo ""
echo "Postgres repo configured."

echo ""
echo "Next step - optional - change the default Postges DB password,"
echo "     application-database and user to be created by making a copy "
echo "     of the sample config file and editing it. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp ../module-config-samples/pbase_postgres11.json ."
echo "  vi pbase_postgres11.json"

echo ""
echo "Next step - install postgres now with:"
echo ""
echo "  yum -y install postgresql11-server"

%preun
echo "rpm preuninstall"

## remove the repo files that were added by script
/bin/rm -f /etc/yum.repos.d/pgdg-*.repo

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-postgres11/etc-pki-rpm-gpg/RPM-GPG-KEY-PGDG
/usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/pgdg-redhat-all.repo
/usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/pgdg-redhat-amzn2.repo
/usr/local/pbase-data/pbase-preconfig-postgres11/etc-yum-repos-d/fedora/pgdg-fedora-all.repo
/usr/local/pbase-data/admin-only/module-config-samples/pbase_postgres11.json