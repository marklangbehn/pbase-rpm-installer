Name: pbase-realtime-kernel
Version: 1.0
Release: 0
Summary: PBase realtime kernel install
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-realtime-kernel
Requires: kernel-rt, rt-setup, rt-tests, rteval

%description
PBase realtime kernel install

%prep

%install

%clean

%pre

%post
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase realtime kernel install"

##TODO require CentOS8 Stream

echo "Next steps:"
echo "  Check kernel :         grubby --default-kernel"
echo "  Tune RT kernel:"
echo "                         tuna"

%files
