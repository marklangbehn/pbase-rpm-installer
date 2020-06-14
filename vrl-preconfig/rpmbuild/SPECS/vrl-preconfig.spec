Name: vrl-preconfig
Version: 1.0
Release: 0
Summary: VirtualRecordLabel.net website bootstrap rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: vrl-preconfig-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: vrl-preconfig

%description
VirtualRecordLabel.net preconfig rpm that adds YUM .repo file pointing to VRL repository

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre
echo "rpm preinstall $1"

%post
echo "rpm postinstall $1"
echo "VRL repo:                /etc/yum.repos.d/vrlsite-content.repo"

echo "Next steps - Install the VirtualRecordLabel sample website content with:"
echo ""
echo "  yum -y install vrl-website-content"

%files
%defattr(-,root,root,-)
/etc/yum.repos.d/vrlsite-content.repo
