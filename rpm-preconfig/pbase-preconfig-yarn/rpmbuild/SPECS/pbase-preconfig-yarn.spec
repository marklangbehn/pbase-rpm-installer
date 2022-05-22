Name: pbase-preconfig-yarn
Version: 1.0
Release: 0
Summary: PBase NodeJS repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-yarn-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-yarn
##Requires: git,curl

%description
Configure yum repo for Yarn

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

echo "PBase Yarn YUM repo pre-configuration"
echo ""

YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-yarn/etc-yum-repos-d"
REPO_NAME="yarn.repo"

if [[ -e "/etc/yum.repos.d/$REPO_NAME" ]]; then
  echo "Existing YUM repo:       /etc/yum.repos.d/$REPO_NAME"
else
  echo "Yarn repo:               /etc/yum.repos.d/$REPO_NAME"
  /bin/cp -f $YUM_REPO_PATH/$REPO_NAME /etc/yum.repos.d/
fi


echo ""
echo "Yarn repo configured."
echo "Next step - yarn now with:"
echo ""
echo "  yum -y install yarn"
echo ""

%preun
echo "rpm preuninstall"

## remove the repo files that were added by script
/bin/rm -f /etc/yum.repos.d/yarn.repo

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-yarn/etc-yum-repos-d/yarn.repo