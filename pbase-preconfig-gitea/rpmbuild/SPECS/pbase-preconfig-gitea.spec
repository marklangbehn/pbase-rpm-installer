Name: pbase-preconfig-gitea
Version: 1.0
Release: 0
Summary: PBase Gitea config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-gitea-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-gitea

%description
Configure PBase Gitea config file

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

echo "PBase Gitea config file create"

## edit-in-place the create-user script
THISDOMAINNAME="$(hostname -d)"
TMPLDOMAINNAME="pbase-foundation.com"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
sed -i -e "s/$TMPLDOMAINNAME/$THISDOMAINNAME/g" ${MODULE_CONFIG_DIR}/pbase_gitea.json

echo ""
echo "PBase Gitea module config file:"
echo "Next step - optional - change the Gitea server default config by"
echo "            editing pbase_gitea.json. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_gitea.json"
echo ""
echo "Next step - install Gitea with:"
echo "  yum -y install pbase-gitea"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/admin-only/module-config.d/pbase_gitea.json
