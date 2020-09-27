Name: pbase-epel
Version: 1.0
Release: 0
Summary: PBase EPEL
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-epel
Requires: pbase-epel-transitive-dep

%description
PBase EPEL

%prep

%install

%clean

%pre

%post
# echo "rpm postinstall $1"

echo "PBase EPEL"

%files
