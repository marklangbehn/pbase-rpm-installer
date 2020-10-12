Name: pbase-timesync-enable-el7-dep
Version: 1.0
Release: 0
Summary: PBase NTP/Chrony Time synchronization transitive dependencies for EL7 and higher
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-timesync-enable-transitive-dep
Requires: chrony

%description
PBase NTP/Chrony Time synchronization transitive dependency for EL7 and higher

%prep

%install

%clean

%pre

%post
# echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase NTP/Chrony Time synchronization transitive dependency for EL7 and higher"

%files
