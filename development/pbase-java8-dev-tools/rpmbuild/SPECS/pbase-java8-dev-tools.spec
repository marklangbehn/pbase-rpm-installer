Name: pbase-java8-dev-tools
Version: 1.0
Release: 0
Summary: PBase Java 8, Maven and other Development Tools rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-java8-dev-tools-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-java8-dev-tools
Requires: java-1.8.0-openjdk-devel,git,perl,rpm-build,vim,mc,nano,curl,wget,tree,zip,unzip,redhat-lsb-core,gcc,gcc-c++,make

%description
Configures Java 8 Development Tools

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

#echo "Installing Ant:           /opt/ant"
#/bin/cp -rf /usr/local/pbase-data/ant /opt

#echo "Installing Maven:         /opt/maven"
#/bin/cp -rf /usr/local/pbase-data/maven /opt

#echo "Installing env-variables: /etc/profile.d"
#/bin/cp -rf /usr/local/pbase-data/pbase-java8-dev-tools/etc-profile-d/*.sh /etc/profile.d

echo "Downloading Maven from apache.org"

DOWNLOADS_DIR="/usr/local/pbase-data/pbase-java8-dev-tools/downloads/"
MAVEN_BIN_URL="https://downloads.apache.org/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz"

mkdir -p "${DOWNLOADS_DIR}"
cd "${DOWNLOADS_DIR}"

## ensure it's not holding an older file
/bin/rm -f *.gz

## download
wget -q ${MAVEN_BIN_URL}
ls -lh *.gz
tar zxf apache-maven-*.gz -C /opt

cd /opt
mv /opt/apache-maven-* /opt/maven

echo "Maven home:              /opt/maven"

echo "Maven env-variables:     /etc/profile.d/pbase-maven.sh"
/bin/cp -rf /usr/local/pbase-data/pbase-java8-dev-tools/etc-profile-d/pbase-maven.sh /etc/profile.d


#echo "The next time you login or reboot, these development tools be available:"
echo "These development tools are now available:"
echo "                         git java mvn perl"

echo ""
echo "These command line utilities are also available:"
echo "                         nano vim mc tree wget curl gcc make zip unzip"
echo ""


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-java8-dev-tools/etc-profile-d/pbase-ant.sh
/usr/local/pbase-data/pbase-java8-dev-tools/etc-profile-d/pbase-java.sh
/usr/local/pbase-data/pbase-java8-dev-tools/etc-profile-d/pbase-maven.sh
