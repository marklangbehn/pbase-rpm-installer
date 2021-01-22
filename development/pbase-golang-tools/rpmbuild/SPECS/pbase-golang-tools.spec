Name: pbase-golang-tools
Version: 1.0
Release: 0
Summary: PBase Go dependencies
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-golang-tools
Requires: git, pbase-golang-transitive-dep

%description
Go dependencies

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

echo "Next steps:              'go' language is ready."

%files
