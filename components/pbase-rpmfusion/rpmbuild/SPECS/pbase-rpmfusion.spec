Name: pbase-rpmfusion
Version: 1.0
Release: 0
Summary: PBase RPMFusion enable rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-rpmfusion
Requires: pbase-epel, rpmfusion-free-release, rpmfusion-nonfree-release

%description
PBase RPMFusion repository enable

%prep

%install

%clean

%pre

%post
# echo "rpm postinstall $1"

echo ""
echo "RPMFusion repository enabled"

echo "To enable additional packages and media codecs run these commands:"
echo ""
echo "  yum -y install rpmfusion-free-release-tainted"
echo "  yum -y install rpmfusion-nonfree-release-tainted"
echo ""

%files
