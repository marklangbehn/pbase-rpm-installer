Name: pbase-preconfig-s3storage
Version: 1.0
Release: 0
Summary: PBase Apache httpd config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-s3storage-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-s3storage
Requires: pbase-epel

%description
Configure S3 Storage dependencies and config file

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

echo "PBase S3 Storage dependencies and pre-config file"

echo ""
echo "Next step - change the default config by making"
echo "    a copy of the config sample file and editing it. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp /usr/local/pbase-data/pbase-preconfig-s3storage/module-config-samples/pbase_s3storage.json ."
echo "  vi pbase_s3storage.json"
echo ""
echo "Next step - finish S3 configuration with:"
echo ""
echo "  yum -y install pbase-s3storage"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-s3storage/module-config-samples/pbase_s3storage.json