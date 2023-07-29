Name: pbase-preconfig-remi-php74
Version: 1.0
Release: 2
Summary: PBase Remi repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-remi-php74-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-remi-php74
Requires: pbase-epel

%description
Configure Remi yum repo for PHP 7.4

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
  AMAZON20XX_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2 ')"
    AMAZON20XX_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 20')"
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
  elif [[ "$AMAZON20XX_RELEASE" != "" ]]; then
    echo "AMAZON20XX_RELEASE:      $AMAZON20XX_RELEASE"
    REDHAT_RELEASE_DIGIT="9"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}

echo "PBase PHP 7.4 pre-configuration"

## check which version of Linux is installed
check_linux_version

## special case for amazon linux 2 - don't add repo, instead use the 'amazon-linux-extras'
if [[ "${AMAZON2_RELEASE}" != "" ]] ; then
  ##echo "AMAZON2_RELEASE:         ${AMAZON2_RELEASE}"
  echo "Not installing Remi repo. Must use Amazon extras command instead."
  echo "Manual step step:"
  echo ""
  echo "  amazon-linux-extras install php7.4"
  echo ""
  echo "Exiting"
  exit 0
fi

## GPG keys are in RPM-GPG-KEY-remi-files.tar
## created with:  tar cf RPM-GPG-KEY-remi-files.tar RPM-GPG-KEY-rem*
echo "Remi rpm-gpg keys:       /etc/pki/rpm-gpg"

if [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]] ; then
  echo "el7:"
  cd  /usr/local/pbase-data/pbase-preconfig-remi-php74/etc-pki-rpm-gpg/el7/
  tar xf RPM-GPG-KEY-remi-files.tar -C /etc/pki/rpm-gpg/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]] ; then
  echo "el8:"
  cd  /usr/local/pbase-data/pbase-preconfig-remi-php74/etc-pki-rpm-gpg/el8/
  tar xf RPM-GPG-KEY-remi-files.tar -C /etc/pki/rpm-gpg/
elif [[ "${FEDORA_RELEASE}" != "" ]] ; then
  echo "fedora:"
  cd  /usr/local/pbase-data/pbase-preconfig-remi-php74/etc-pki-rpm-gpg/fedora/
  tar xf RPM-GPG-KEY-remi-files.tar -C /etc/pki/rpm-gpg/
else
  echo "Leaving unchanged"
fi


echo "Remi yum repos"
cd  /usr/local/pbase-data/pbase-preconfig-remi-php74/etc-yum-repos-d/

if [[ -e "/etc/yum.repos.d/remi-safe.repo" ]] ; then
  echo "Existing remi-safe.repo found, leaving unchanged"
elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]] ; then
  echo "el6:"
  tar xf ./el6/REMI-REPOS-el6.tar -C /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]] ; then
  echo "el7:"
  tar xf ./el7/REMI-REPOS-el7.tar -C /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]] ; then
  echo "el8:"
  tar xf ./el8/REMI-REPOS-el8.tar -C /etc/yum.repos.d/
elif [[ "${FEDORA_RELEASE}" != "" ]] ; then
  echo "fedora:"
  tar xf ./fedora/REMI-REPOS-fedora.tar -C /etc/yum.repos.d/
else
  echo "Leaving unchanged"
fi

if [[ -e "/etc/yum.repos.d/remi.repo" ]] ; then
  ls -l /etc/yum.repos.d/remi*.repo
  echo ""
  echo "Remi repo configured."
  echo ""
fi


%preun
echo "rpm preuninstall"

## remove the repo files added by script
/bin/rm -f /etc/yum.repos.d/remi.repo
/bin/rm -f /etc/yum.repos.d/remi-*.repo

if [[ -e "/etc/yum.repos.d/amzn2extra-php72.repo" ]]; then
  echo "Removing yum repo:       amzn2extra-php72.repo"
  /bin/rm -f /etc/yum.repos.d/amzn2extra-php72.repo
fi

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-remi-php74/etc-yum-repos-d/el6/REMI-REPOS-el6.tar
/usr/local/pbase-data/pbase-preconfig-remi-php74/etc-yum-repos-d/el7/REMI-REPOS-el7.tar
/usr/local/pbase-data/pbase-preconfig-remi-php74/etc-yum-repos-d/el8/REMI-REPOS-el8.tar
/usr/local/pbase-data/pbase-preconfig-remi-php74/etc-yum-repos-d/fedora/REMI-REPOS-fedora.tar
/usr/local/pbase-data/pbase-preconfig-remi-php74/etc-pki-rpm-gpg/el7/RPM-GPG-KEY-remi-files.tar
/usr/local/pbase-data/pbase-preconfig-remi-php74/etc-pki-rpm-gpg/el8/RPM-GPG-KEY-remi-files.tar
/usr/local/pbase-data/pbase-preconfig-remi-php74/etc-pki-rpm-gpg/fedora/RPM-GPG-KEY-remi-files.tar
