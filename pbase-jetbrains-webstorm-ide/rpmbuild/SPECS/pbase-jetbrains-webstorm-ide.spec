Name: pbase-jetbrains-webstorm-ide
Version: 1.0
Release: 0
Summary: PBase Jetbrains Webstorm JavaScript IDE download rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-jetbrains-webstorm-ide-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-jetbrains-webstorm-ide
Requires: git,curl

%description
Jetbrains Webstorm JavaScript IDE download

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

copy_if_not_exists() {
  if [ -z "$1" ]  ||  [ -z "$2" ]  ||  [ -z "$3" ]; then
    echo "All 3 params must be passed to %post.copy_if_not_exists function"
    exit 1
  fi

  FILENAME="$1"
  SOURCE_DIR="$2"
  DEST_DIR="$3"

  SOURCE_FILE_PATH=$SOURCE_DIR/$FILENAME
  DEST_FILE_PATH=$DEST_DIR/$FILENAME

  if [[ -f "$DEST_FILE_PATH" ]] ; then
    echo "Already exists:          $DEST_FILE_PATH"
    return 0
  else
    echo "Copying file:            $DEST_FILE_PATH"
    /bin/cp -rf --no-clobber $SOURCE_FILE_PATH  $DEST_DIR
    return 1
  fi
}


echo "PBase JetBrains Webstorm IDE download"
echo ""

## check if already installed
if [[ -d "/opt/WebStorm" ]]; then
  echo "/opt/WebStorm directory already exists"
  exit 0
fi

## check if inotify setting already done
INOTIFY_FILE="inotify-maxuserwatches.conf"
INOTIFY_SRC_CONF_PATH="/usr/local/pbase-data/pbase-jetbrains-intellij-ide/etc-sysctl-d"
ETC_SYSCTL_D_PATH="/etc/sysctl.d"

INOTIFY_FILE_EXISTS=$(copy_if_not_exists $INOTIFY_FILE $INOTIFY_SRC_CONF_PATH $ETC_SYSCTL_D_PATH)
## echo "returned $?:             $?"

if [[ $? == "1" ]] ; then
  echo "inotify setting:         /etc/profile.d/inotify-maxuserwatches.conf"
  echo "                         fs.inotify.max_user_watches = 524288"

  echo "Calling:                 sysctl -p --system"
  sysctl -p --system
fi

echo "Downloading Webstorm from jetbrains.com"

cd /usr/local/pbase-data/pbase-jetbrains-webstorm-ide

wget -q https://download.jetbrains.com/webstorm/WebStorm-2020.1.tar.gz

echo "Downloaded file from jetbrains.com:"
ls -lh /usr/local/pbase-data/pbase-jetbrains-webstorm-ide/*.gz
tar zxf WebStorm-*.tar.gz -C /opt

echo "Unzipped into /opt"

cd /opt
mv /opt/WebStorm-* /opt/WebStorm

#echo "Adding env-variables:    /etc/profile.d/pbase-webstorm.sh"
#/bin/cp -rf /usr/local/pbase-data/pbase-jetbrains-webstorm-ide/etc-profile-d/*.sh /etc/profile.d
#echo "To re-load now:          source /etc/profile.d/pbase-webstorm.sh"
#echo ""

echo "Next step - as root, change the owner of the IDE directory:"
echo "       '/opt/WebStorm' to the desktop user"
echo ""
echo "  chown -R mydesktopusername:mydesktopusername /opt/WebStorm"
echo ""
echo "     Then login as the desktop user and launch the installation wizard"
echo ""
echo "  cd /opt/WebStorm/bin"
echo "  ./webstorm.sh"
echo ""
echo "After completing the installation wizard the Webstorm IDE is ready to use"

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-jetbrains-webstorm-ide/etc-sysctl-d/inotify-maxuserwatches.conf
/usr/local/pbase-data/pbase-jetbrains-webstorm-ide/etc-profile-d/pbase-webstorm.sh
