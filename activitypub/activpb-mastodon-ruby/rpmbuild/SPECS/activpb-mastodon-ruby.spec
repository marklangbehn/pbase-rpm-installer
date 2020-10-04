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


echo "PBase Mastodon Ruby and Dependencies"

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

echo "Execute Install:         rbenv install 2.6.6"

su - mastodon -c "RUBY_CONFIGURE_OPTS=\"--with-jemalloc-prefix\" rbenv install 2.6.6"
su - mastodon -c "rbenv global 2.6.6"

echo "Mastodon Ruby and Dependencies installed"

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/activpb-mastodon-ruby/ruby-bashrc.sh
