Name: activpb-mastodon-ruby
Version: 1.0
Release: 3
Summary: PBase Mastodon Ruby and Dependencies rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: activpb-mastodon-ruby-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: activpb-mastodon-ruby
Requires: redis, yarn, redhat-rpm-config, nodejs, nginx, tar, jq, curl, git, gpg, git-core, zlib, zlib-devel, gcc, gcc-c++, patch, readline, readline-devel, libffi-devel, openssl-devel, jemalloc-devel, postgresql-devel, make, pkgconfig, autoconf, automake, libtool, bison, curl, sqlite-devel, libxml2-devel, libxslt-devel, libyaml-devel, gdbm-devel, ncurses-devel, glibc-headers, libidn, libidn-devel, glibc-devel, libicu-devel, libpq-devel, protobuf, protobuf-devel, protobuf-compiler, bzip2, ImageMagick, certbot, python3-certbot-nginx, pbase-firewall-enable, perl, perl-FindBin, pbase-firewall-enable

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

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## Mastodon config
## look for config file "activpb_mastodon.json"
PBASE_CONFIG_FILENAME="activpb_mastodon.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
## version to download
parseConfig "MASTODON_VER_CONFIG" ".activpb_mastodon.mastodonVersion" ""

# disable git message
git config --global advice.detachedHead false

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

echo "Executing:               git config --global --add safe.directory /home/mastodon/live"

## do as mastodon user
su - mastodon -c "git config --global --add safe.directory /home/mastodon/live"

## do as root user
git config --global --add safe.directory /home/mastodon/live

echo "Execute configure and make"
su - mastodon -c "cd /home/mastodon/.rbenv && src/configure && make -C src"

echo "Configuring shell to load rbenv"
echo 'eval "$(~/.rbenv/bin/rbenv init - bash)"' >> /home/mastodon/.bash_profile
chown mastodon:mastodon /home/mastodon/.bash_profile

#echo "Add rbenv lines .bashrc"
#cat /home/mastodon/.bashrc /usr/local/pbase-data/activpb-mastodon-ruby/ruby-bashrc.sh  >  /home/mastodon/.bashrc-rbenv
#/bin/cp -f /home/mastodon/.bashrc-rbenv /home/mastodon/.bashrc
#chown mastodon:mastodon /home/mastodon/.bashrc
#source /home/mastodon/.bashrc

echo "Pull code for rbenv/plugins"
su - mastodon -c "source /home/mastodon/.bash_profile  &&  git clone https://github.com/rbenv/ruby-build.git /home/mastodon/.rbenv/plugins/ruby-build"


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


# turn off git message
su - mastodon -c "git config --global advice.detachedHead false"

# checkout release version
if [[ "${VERSION}" != "HEAD" ]] && [[ "${VERSION}" != "head" ]] ; then
  su - mastodon -c "cd /home/mastodon/live  ;  git checkout ${VERSION}"
fi

## use the version number stored in text file
RUBY_VERSION="3.2.2"
RUBY_VERSION_FILE="/home/mastodon/live/.ruby-version"
if [[ -e "${RUBY_VERSION_FILE}" ]] ; then
  echo "Found:                   ${RUBY_VERSION_FILE}"
  read -r RUBY_VERSION < "${RUBY_VERSION_FILE}"
fi

echo "Execute Install:         rbenv install ${RUBY_VERSION}"
su - mastodon -c "RUBY_CONFIGURE_OPTS=\"--with-jemalloc-prefix\" rbenv install ${RUBY_VERSION}"
su - mastodon -c "rbenv global ${RUBY_VERSION}"

echo "Mastodon Ruby and Dependencies installed"

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/activpb-mastodon-ruby/ruby-bashrc.sh
