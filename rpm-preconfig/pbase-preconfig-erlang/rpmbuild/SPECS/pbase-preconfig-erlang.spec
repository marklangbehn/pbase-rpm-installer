Name: pbase-preconfig-erlang
Version: 1.0
Release: 0
Summary: PBase NodeJS repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-erlang-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-erlang
Requires: pbase-epel

%description
Configure yum repo for Elang and Elixir

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


echo "PBase Erlang YUM repo pre-configuration"
echo ""

# check which version of Linux is installed
check_linux_version

YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-erlang/etc-yum-repos-d/"
REPO_NAME="erlang-solutions.repo"

if [[ -e "/etc/yum.repos.d/$REPO_NAME" ]]; then
  echo "Existing YUM repo:       /etc/yum.repos.d/$REPO_NAME"
else
  echo "nodesource repo:         /etc/yum.repos.d/$REPO_NAME"
  /bin/cp -f $YUM_REPO_PATH/$REPO_NAME /etc/yum.repos.d/
fi


echo ""
echo "Erlang and Elixir repo configured."
echo "Next step - install Erlang now with:"
echo ""
echo "  yum -y install erlang erlang-parsetools erlang-xmerl"
echo ""

%preun
echo "rpm preuninstall"

## remove the repo file added by script
/bin/rm -f /etc/yum.repos.d/erlang-solutions.repo

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-erlang/etc-yum-repos-d/erlang-solutions.repo