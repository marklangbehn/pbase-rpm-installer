Name: activpb-mastodon-ruby
Version: 1.0
Release: 0
Summary: PBase Mastodon Ruby and Dependencies rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: activpb-mastodon-ruby-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: activpb-mastodon-ruby
Requires: redis, yarn, protobuf-devel, redhat-rpm-config, nodejs, nginx, tar, jq, curl, git, gpg, gcc, git-core, zlib, zlib-devel, gcc-c++, patch, readline, readline-devel, libffi-devel, openssl-devel, make, autoconf, automake, libtool, bison, curl, sqlite-devel, libxml2-devel, libxslt-devel, gdbm-devel, ncurses-devel, glibc-headers, libidn, libidn-devel, glibc-devel, libicu-devel, protobuf, bzip2, ImageMagick, certbot

%description
PBase Mastodon service

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

locateConfigFile() {
  ## name of config file is passed in param $1 - for example "activpb_mastodon.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.json"
  PBASE_CONFIG_DIR="${PBASE_CONFIG_BASE}/module-config.d"

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

echo "PBase Mastodon Ruby and Dependencies"

## Mastodon config
## look for either separate config file "activpb_mastodon.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="activpb_mastodon.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
## version to download
parseConfig "MASTODON_VER_CONFIG" ".activpb_mastodon.mastodonVersion" ""

## USER
echo "Creating group and user: mastodon"

adduser \
   --system \
   --shell /bin/bash \
   --comment 'Mastodon service' \
   --user-group \
   --home /home/mastodon -m \
   mastodon

## must let other users see the contents too - needed for nginx access permissions
chmod +x /home/mastodon

## RUBY
## pull env and code
echo "Pull code for rbenv"
su - mastodon -c "cd /home/mastodon/  &&  git clone https://github.com/rbenv/rbenv.git /home/mastodon/.rbenv"

echo "Execute configure and make"
su - mastodon -c "cd /home/mastodon/.rbenv && src/configure && make -C src"

echo "Add rbenv lines .bashrc"

cat /home/mastodon/.bashrc /usr/local/pbase-data/activpb-mastodon-ruby/ruby-bashrc.sh  >  /home/mastodon/.bashrc-rbenv
/bin/cp -f /home/mastodon/.bashrc-rbenv /home/mastodon/.bashrc
chown mastodon:mastodon /home/mastodon/.bashrc

echo "Pull code for rbenv/plugins"
su - mastodon -c "source /home/mastodon/.bashrc  &&  git clone https://github.com/rbenv/ruby-build.git /home/mastodon/.rbenv/plugins/ruby-build"


## PULL SOURCE CODE
cd /home/mastodon/
su - mastodon -c "git clone https://github.com/tootsuite/mastodon.git live"

cd /home/mastodon/live/
VERSION=""
echo "Checkout git tag for"

if [[ "${MASTODON_VER_CONFIG}" != "" ]]; then
  VERSION="${MASTODON_VER_CONFIG}"
  echo "Configured version:      ${MASTODON_VER_CONFIG}"
else
  VERSION=$(git tag -l | grep -v 'rc[0-9]*$' | sort -V | tail -n 1)
  echo "Latest version:          ${VERSION}"
fi

su - mastodon -c "cd /home/mastodon/live  ;  git checkout ${VERSION}"


## use the version number stored in text file
RUBY_VERSION="2.7.2"
RUBY_VERSION_FILE="/home/mastodon/live/.ruby-version"
if [[ -e "${RUBY_VERSION_FILE}" ]] ; then
  echo "Found:                   ${RUBY_VERSION_FILE}"
  read -r RUBY_VERSION < "${RUBY_VERSION_FILE}"
fi

echo "Execute Install:         rbenv install ${RUBY_VERSION}"
su - mastodon -c "RUBY_CONFIGURE_OPTS=\"--with-jemalloc-prefix\" rbenv install ${RUBY_VERSION}"
su - mastodon -c "rbenv global ${RUBY_VERSION}"

#echo "Execute Install:         rbenv install 2.7.2"
#su - mastodon -c "RUBY_CONFIGURE_OPTS=\"--with-jemalloc-prefix\" rbenv install 2.7.2"
#su - mastodon -c "rbenv global 2.7.2"

echo "Mastodon Ruby and Dependencies installed"

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/activpb-mastodon-ruby/ruby-bashrc.sh
