Name: pbase-preconfig-apache
Version: 1.0
Release: 0
Summary: PBase Apache httpd config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-apache-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-apache

%description
Configure Apache httpd config file

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

echo "PBase Apache httpd config file create"

echo ""
echo "PBase Apache module config file:"
echo "Next step - optional - change the Apache server default config by making"
echo "    a copy of the config sample file and editing it. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp ../module-config-samples/pbase_apache.json ."
echo "  vi pbase_apache.json"
echo ""
echo "Next step - install Apache with:"
echo ""
echo "  yum -y install pbase-apache"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/admin-only/module-config-samples/pbase_apache.json