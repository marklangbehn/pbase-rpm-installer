Name: activpb-mastodon-bundle
Version: 1.0
Release: 0
Summary: PBase Mastodon service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: activpb-mastodon-bundle
Requires: activpb-mastodon-ruby

%description
PBase Mastodon Ruby bundler

%prep

%install

%clean

%pre

%post
# echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase Mastodon Ruby bundler"

## check if installed
if [[ ! -d "/home/mastodon" ]]; then
  echo "/home/mastodon directory not found - exiting"
  exit 0
fi


echo "Checking rbenv"
su - mastodon -c "rbenv --version"

echo "Checking out Mastodon source code from github"
echo "Mastodon code:           /home/mastodon/live"

## PULL SOURCE CODE
cd /home/mastodon/
su - mastodon -c "git clone https://github.com/tootsuite/mastodon.git live"

cd /home/mastodon/live/
echo "Checkout latest release:"
su - mastodon -c "cd /home/mastodon/live  ;  git checkout $(git tag -l | grep -v 'rc[0-9]*$' | sort -V | tail -n 1)"

echo ""

## BUNDLER
echo "Configure Ruby bundler"

su - mastodon -c "cd /home/mastodon/live  ;  gem install bundler --no-document"

su - mastodon -c "cd /home/mastodon/live  ;  bundle config deployment 'true'"
su - mastodon -c "cd /home/mastodon/live  ;  bundle config without 'development test'"

echo ""
echo "Executing bundle config build.pg"

su - mastodon -c "cd /home/mastodon/live  ;  bundle config build.pg --with-pg-config=/usr/bin/pg_config"

echo "Executing bundle install..."

su - mastodon -c "cd /home/mastodon/live  ;  bundle install -j$(getconf _NPROCESSORS_ONLN)"
su - mastodon -c "cd /home/mastodon/live  ;  yarn install --pure-lockfile"

echo "Mastodon code bundle:    /home/mastodon/live"

%files