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
Requires: git, curl, jq

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

## config is stored in json file with root-only permissions
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.json"
  PBASE_CONFIG_DIR="${PBASE_CONFIG_BASE}/module-config.d"

  ## config is stored in json file with root-only permissions
  ##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/

  PBASE_CONFIG_SEPARATE="${PBASE_CONFIG_DIR}/${PBASE_CONFIG_FILENAME}"
  PBASE_CONFIG_ALLINONE="${PBASE_CONFIG_BASE}/${PBASE_ALL_IN_ONE_CONFIG_FILENAME}"

  #echo "PBASE_CONFIG_SEPARATE:   $PBASE_CONFIG_SEPARATE"
  #echo "PBASE_CONFIG_ALLINONE:   $PBASE_CONFIG_ALLINONE"

  ## check if either file exists, assume SEPARATE as default
  PBASE_CONFIG="$PBASE_CONFIG_SEPARATE"

  if [[ -f "$PBASE_CONFIG_ALLINONE" ]] ; then
    PBASE_CONFIG="$PBASE_CONFIG_ALLINONE"
  fi

  if [[ -f "$PBASE_CONFIG" ]] ; then
    echo "Config file found:       $PBASE_CONFIG"
  else
    echo "Custom config not found: $PBASE_CONFIG"
  fi
}


parseConfig() {
  ## fallback when jq is not installed, use the default in the third param
  HAS_JQ_INSTALLED="$(which jq)"
  #echo "HAS_JQ_INSTALLED:   $HAS_JQ_INSTALLED"

  if [[ -z "$HAS_JQ_INSTALLED" ]] || [[ ! -f "$PBASE_CONFIG" ]] ; then
    ## echo "fallback to default: $3"
    eval "$1"="$3"
    return 1
  fi

  ## use jq to extract a json field named in the second param
  PARSED_VALUE="$(cat $PBASE_CONFIG  |  jq $2)"

  ## use eval to assign that to the variable named in the first param
  eval "$1"="$PARSED_VALUE"
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


echo "PBase JetBrains Webstorm IDE download"
echo ""

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for config file like "pbase_repo.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_DESKTOP_USER_NAME" ".pbase_repo.defaultDesktopUsername" ""

DESKTOP_USER_NAME="mydesktopusername"
if [[ "$DEFAULT_DESKTOP_USER_NAME" != "" ]] && [[ "$DEFAULT_DESKTOP_USER_NAME" != null ]]; then
  echo "defaultDesktopUsername:  $DEFAULT_DESKTOP_USER_NAME"
  DESKTOP_USER_NAME="$DEFAULT_DESKTOP_USER_NAME"
fi

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

wget -q https://download.jetbrains.com/webstorm/WebStorm-2020.3.2.tar.gz

echo "Downloaded file from jetbrains.com:"
ls -lh /usr/local/pbase-data/pbase-jetbrains-webstorm-ide/*.gz
tar zxf WebStorm-*.tar.gz -C /opt

echo "Unzipped into /opt"

cd /opt
mv /opt/WebStorm-* /opt/WebStorm

## set permission for desktop user
if [[ "$DEFAULT_DESKTOP_USER_NAME" != "" ]] && [[ "$DEFAULT_DESKTOP_USER_NAME" != null ]]; then
  echo "chown -R $DEFAULT_DESKTOP_USER_NAME:$DEFAULT_DESKTOP_USER_NAME /opt/WebStorm"
  chown -R $DEFAULT_DESKTOP_USER_NAME:$DEFAULT_DESKTOP_USER_NAME /opt/WebStorm
fi

#echo "Adding env-variables:    /etc/profile.d/pbase-webstorm.sh"
#/bin/cp -rf /usr/local/pbase-data/pbase-jetbrains-webstorm-ide/etc-profile-d/*.sh /etc/profile.d
#echo "To re-load now:          source /etc/profile.d/pbase-webstorm.sh"
#echo ""

echo "Next step - if needed - as root, change the owner of the IDE directory:"
echo "       '/opt/WebStorm' to the desktop user"
echo ""
echo "  chown -R $DESKTOP_USER_NAME:$DESKTOP_USER_NAME /opt/WebStorm"
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
