Name: pbase-preconfig-chrome
Version: 1.0
Release: 0
Summary: PBase Google Chrome repo preconfig rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-chrome-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-chrome

%description
PBase desktop applications preconfig rpm that adds YUM .repo file for Google Chrome

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
echo "Added yum repo:          google-chrome.repo"



echo "Next step - Install Chrome with:"
echo ""
echo "  yum -y install google-chrome-stable"
echo ""

%files
%defattr(-,root,root,-)
/etc/yum.repos.d/google-chrome.repo
