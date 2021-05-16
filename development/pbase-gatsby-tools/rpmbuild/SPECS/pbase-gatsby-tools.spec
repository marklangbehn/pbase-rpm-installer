Name: pbase-gatsby-tools
Version: 1.0
Release: 1
Summary: PBase Gatsby JS dependencies
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-gatsby-tools
Requires: git, autoconf, libtool, pkgconfig, wget, curl, bzip2, make, gcc-c++, pbase-gatsby-tools-transitive-dep, pbase-preconfig-yarn

%description
Gatsby JS dependencies

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


if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi


echo "Gatsby JS command line"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

echo "executing:               npm install --global gatsby-cli"
echo ""

npm install --global gatsby-cli

#echo ""
#echo "executing:               gatsby telemetry --disable"
#gatsby telemetry --disable
echo "Next steps:              Put your git source credentials in the file: ~/.netrc"
echo "                         then, clone and build your site."
echo ""

%files
