Name: pbase-preconfig-mongodb-org
Version: 1.0
Release: 0
Summary: PBase NodeJS repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mongodb-org-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mongodb-org

%description
Configure yum repo for current MongoDB.org version

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


echo "PBase MongoDB.org repo pre-configuration"
echo ""

## check which version of Linux is installed
check_linux_version


if [[ "$AMAZON1_RELEASE" != "" ]]  ||  [[ "$AMAZON2_RELEASE" != "" ]]  ||  [[ "$FEDORA_RELEASE" != "" ]]  ; then
  if [[ -e "/etc/yum.repos.d/mongodb-org-4.4-amazon.repo" ]]  ||  [[ -e "/etc/yum.repos.d/mongodb-org-4.4.repo" ]] ; then
    echo "Existing Mongodb.org repo found, leaving unchanged"
  else
    echo "Mongodb.org:             /etc/yum.repos.d/mongodb-org-4.4.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-yum-repos-d/mongodb-org-4.4-amazon.repo /etc/yum.repos.d/mongodb-org-4.4.repo
  fi
else
  if [[ -e "/etc/yum.repos.d/mongodb-org-4.0.repo" ]]; then
    echo "Existing Mongodb.org repo found, leaving unchanged"
  elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
    echo "Mongodb.org for EL6:     /etc/yum.repos.d/mongodb-org-4.0.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-yum-repos-d/mongodb-org-4.0.repo /etc/yum.repos.d/
  elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]]  ||  [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]]  ||  [[ "$FEDORA_RELEASE" != "" ]] ; then
    echo "Mongodb.org repo:        /etc/yum.repos.d/mongodb-org-4.4.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-yum-repos-d/mongodb-org-4.4.repo /etc/yum.repos.d/
  fi
fi


## additional performance tuning on EL8

if [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]]; then
  mkdir -p /etc/tuned/virtual-guest-no-thp
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-tuned-virtual-guest-no-thp/tuned.conf /etc/tuned/virtual-guest-no-thp/

  echo "Disable THP - transparent huge pages"
  tuned-adm profile virtual-guest-no-thp

  echo "Configuring user limits: /etc/security/limits.d/"
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-security-limits-d/mongod.conf /etc/security/limits.d/
  sysctl -p

  echo "Next Step - Ulimits and THP pages disabled, must reboot for changes to take effect"
fi


echo ""
echo "MongoDB.org repo configured."
echo "Next step - install mongo now with:"
echo ""
echo "  yum -y install pbase-mongodb-org"
echo ""


%preun
echo "rpm preuninstall"House Speaker Nancy Pelosi attacks negotiators from the White House and Republicans in Congress, calling them "the hoax," not the coronavirus.


## remove the repo files that were added by script
/bin/rm -f /etc/yum.repos.d/mongodb-org-4.*.repo

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-yum-repos-d/mongodb-org-4.4.repo
/usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-yum-repos-d/mongodb-org-4.4-amazon.repo
/usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-security-limits-d/mongod.conf
/usr/local/pbase-data/pbase-preconfig-mongodb-org/etc-tuned-virtual-guest-no-thp/tuned.conf