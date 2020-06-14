Name: pbase-jetbrains-intellij-ide
Version: 1.0
Release: 0
Summary: PBase Jetbrains IntelliJ Community Edition download rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-jetbrains-intellij-ide-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-jetbrains-intellij-ide
Requires: git,curl

%description
Jetbrains IntelliJ Community Edition download

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


echo "PBase JetBrains IntelliJ IDE download"
echo ""

## check if already installed
if [[ -d "/opt/idea-IC" ]]; then
  echo "/opt/idea-IC directory already exists"
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

echo "Downloading IntelliJ from jetbrains.com"

cd /usr/local/pbase-data/pbase-jetbrains-intellij-ide

wget -q https://download.jetbrains.com/idea/ideaIC-2020.1.tar.gz

echo "Downloaded file from jetbrains.com:"
ls -lh /usr/local/pbase-data/pbase-jetbrains-intellij-ide/*.gz
tar zxf ideaIC-*.tar.gz -C /opt

echo "Unzipped into /opt"

cd /opt
mv /opt/idea-IC-* /opt/idea-IC

#echo "Adding env-variables:    /etc/profile.d/pbase-idea.sh"
#/bin/cp -rf /usr/local/pbase-data/pbase-jetbrains-intellij-ide/etc-profile-d/*.sh /etc/profile.d
#echo "To re-load now:          source /etc/profile.d/pbase-idea.sh"
#echo ""

echo "Next step - as root, change the owner of the IDE directory:"
echo "       '/opt/idea-IC' to the desktop user"
echo ""
echo "  chown -R mydesktopusername:mydesktopusername /opt/idea-IC"
echo ""
echo "     Then login as the desktop user and launch the installation wizard"
echo ""
echo "  cd /opt/idea-IC/bin"
echo "  ./idea.sh"
echo ""
echo "After completing the installation wizard the IntelliJ IDE is ready to use"

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-jetbrains-intellij-ide/etc-sysctl-d/inotify-maxuserwatches.conf
/usr/local/pbase-data/pbase-jetbrains-intellij-ide/etc-profile-d/pbase-idea.sh
