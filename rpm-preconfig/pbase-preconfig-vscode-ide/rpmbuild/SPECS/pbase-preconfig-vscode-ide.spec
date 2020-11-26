Name: pbase-preconfig-vscode-ide
Version: 1.0
Release: 0
Summary: PBase VSCode repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-vscode-ide-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-vscode-ide
Requires: git,curl

%description
Configure yum repo for Microsoft VSCode

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
    echo "All 3 params must be passed to copy_if_not_exists function"
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


echo "PBase pre-configuration for MS VSCode YUM repo"
echo ""

## check if inotify setting already done
INOTIFY_FILE="inotify-maxuserwatches.conf"
INOTIFY_SRC_CONF_PATH="/usr/local/pbase-data/pbase-jetbrains-intellij-ide/etc-sysctl-d"
ETC_SYSCTL_D_PATH="/etc/sysctl.d"

INOTIFY_FILE_EXISTS=$(copy_if_not_exists $INOTIFY_FILE $INOTIFY_SRC_CONF_PATH $ETC_SYSCTL_D_PATH)
##echo "returned $?:             $?"

if [[ $? == "1" ]] ; then
  echo "inotify setting:         /etc/profile.d/inotify-maxuserwatches.conf"
  echo "                         fs.inotify.max_user_watches = 524288"

  echo "Calling:                 sysctl -p --system"
  sysctl -p --system
fi

#YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-vscode-ide/etc-yum-repos-d"
#REPO_NAME="vscode.repo"
#if [[ -e "/etc/yum.repos.d/$REPO_NAME" ]]; then
#  echo "Existing YUM repo:       /etc/yum.repos.d/$REPO_NAME"
#else
#  echo "VSCode repo:             /etc/yum.repos.d/$REPO_NAME"
#  /bin/cp -f $YUM_REPO_PATH/$REPO_NAME /etc/yum.repos.d/
#fi

echo ""
echo "Microsoft Visual Studio Code YUM repo configured."
echo "Next step - install VSCode now with:"
echo ""
echo "  yum -y install code"
echo ""
echo "    ... then you can simply launch VSCode anytime: as your desktop user"
echo "        just 'cd' to your source code directory and type in: code ."
echo ""
echo "  cd myprojectdirectory"
echo "  code ."
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-preconfig-vscode-ide/etc-sysctl-d/inotify-maxuserwatches.conf
/etc/yum.repos.d/vscode.repo
