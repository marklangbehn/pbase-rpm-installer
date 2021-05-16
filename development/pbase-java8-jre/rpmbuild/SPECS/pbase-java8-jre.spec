Name: pbase-java8-jre
Version: 1.0
Release: 1
Summary: PBase Java 8, Maven and other Development Tools rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-java8-jre-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-java8-jre
Requires: java-1.8.0-openjdk

%description
Configures Java 8 JRE

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
# echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase Java 8 JRE and JAVA_HOME environment-variable"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi
echo "Installing JAVA_HOME env-variable in: /etc/profile.d"
/bin/cp -rf /usr/local/pbase-data/pbase-java8-jre/etc-profile-d/*.sh /etc/profile.d


echo "The Java 8 JRE is now available:"
echo "                         java"



%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-java8-jre/etc-profile-d/pbase-java.sh

