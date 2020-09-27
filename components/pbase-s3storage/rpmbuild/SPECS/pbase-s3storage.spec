Name: pbase-s3storage
Version: 1.0
Release: 0
Summary: PBase S3 Storage Mount
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-s3storage
Requires: fuse, s3fs-fuse

%description
PBase S3 Storage Mount

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

echo "PBase S3 Storage"
echo ""


%files
