Name: pbase-apache
Version: 1.0
Release: 0
Summary: PBase Apache rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-apache-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-apache
Requires: httpd,apr,apr-util,mod_proxy_html,jq

%description
Configures and start basic Apache httpd service and page

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

append_bashrc_alias() {
  if [ -z "$1" ]  ||  [ -z "$2" ]; then
    echo "Both params must be passed to postinstall.append_bashrc_alias()"
    exit 1
  fi

  EXISTING_ALIAS=$(grep $1 /root/.bashrc)
  if [[ "$EXISTING_ALIAS" == "" ]]; then
    echo "Adding shell alias:  $1"
    echo "alias $1='$2'"  >>  /root/.bashrc
  else
    echo "Already has shell alias '$1' in: /root/.bashrc"
  fi
}

check_linux_version() {
  AMAZON1_RELEASE=""
  AMAZON2_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2')"
    echo "system-release:          ${SYSTEM_RELEASE}"
  fi

  FEDORA_RELEASE=""
  if [[ -e "/etc/fedora-release" ]]; then
    FEDORA_RELEASE="$(cat /etc/fedora-release)"
    echo "fedora_release:          ${FEDORA_RELEASE}"
  fi

  REDHAT_RELEASE_DIGIT=""
  if [[ -e "/etc/redhat-release" ]]; then
    REDHAT_RELEASE_DIGIT="$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n1)"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "AMAZON1_RELEASE:         $AMAZON1_RELEASE"
    REDHAT_RELEASE_DIGIT="6"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON2_RELEASE" != "" ]]; then
    echo "AMAZON2_RELEASE:         $AMAZON2_RELEASE"
    REDHAT_RELEASE_DIGIT="7"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}


echo "PBase Apache"

## config may be stored in json file with root-only permissions
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_apache.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
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

addSelfToEtcHostsFile() {
  echo "addSelfToEtcHostsFile()"
  ## IPADDRESS=`ifconfig eth0 | grep "inet addr" | cut -f2 -d: | cut -f1 -d' '`
  ## IPADDRESS=`hostname  -I | cut -f1 -d' '`

  IPADDRESSLINE=$(ip route get 8.8.8.8 | head -n1)
  echo "IPADDRESSLINE:           ${IPADDRESSLINE}"

  IPADDRESS=$(ip route get 8.8.8.8 | head -n1 | sed 's/ uid 0\s*//' | awk '/8.8.8.8/ {print $NF}')
  FULLHOSTNAME=`hostname`

  ## Update the /etc/hosts file with the current hostname
  if [[ "$FULLHOSTNAME" == "localhost.localdomain" ]]; then
    echo "Hostname not set:        $FULLHOSTNAME"
    ##echo "Not changing /etc/hosts"
  else
    ONLYHOSTNAME=`echo $FULLHOSTNAME  |  cut -d. -f 1`
    echo "ONLYHOSTNAME:            $ONLYHOSTNAME"

    HOSTSLINE="$IPADDRESS $FULLHOSTNAME $ONLYHOSTNAME"

    ## REVISIT not on AWS because AWS act differently for "ip route get 8.8.8.8"
    ## HOSTSLINE="#${HOSTSLINE}"
    HOSTSLINE="${HOSTSLINE}"
    echo "HOSTSLINE:               $HOSTSLINE"

    EXISTINGHOSTNAME=`grep "$ONLYHOSTNAME" /etc/hosts`
    echo "EXISTINGHOSTNAME:   $EXISTINGHOSTNAME"

    if [[ "$EXISTINGHOSTNAME" == "" ]]; then
      echo "Updating file:           /etc/hosts"
      echo "Augeas edit host-line:   $HOSTSLINE"
      #echo $HOSTSLINE >> /etc/hosts

cat <<EOF | augtool --noautoload
set /augeas/load/Hosts
set /augeas/load/Hosts/lens "Hosts.lns"
set /augeas/load/Hosts/incl "/etc/hosts"
load
set /files/etc/hosts/01/ipaddr $IPADDRESS
set /files/etc/hosts/01/canonical $FULLHOSTNAME
set /files/etc/hosts/01/alias[1] $ONLYHOSTNAME
save
EOF

    else
      echo "Already has name in:     /etc/hosts"
    fi
  fi
}

## look for config file "pbase_apache.json"
PBASE_CONFIG_FILENAME="pbase_apache.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "ADD_SELF_TO_ETC_HOSTS" ".pbase_apache.addSelfToEtcHosts" "false"
parseConfig "ADD_SECURITY_HEADERS" ".pbase_apache.addSecurityHeaders" "true"
parseConfig "RESTRICT_HTTP_METHODS" ".pbase_apache.restrictHttpMethods" "false"
parseConfig "USE_SITES_ENABLED_CONF" ".pbase_apache.useSitesEnabledConf" "false"
parseConfig "ENABLE_INDEX_PHP" ".pbase_apache.enableIndexPhp" "false"

parseConfig "SERVER_ADMIN_EMAIL" ".pbase_apache.serverAdmin" "nobody@nowhere.nyet"
parseConfig "SUBDOMAIN_NAME" ".pbase_apache.urlSubDomain" ""

echo "ADD_SELF_TO_ETC_HOSTS:   $ADD_SELF_TO_ETC_HOSTS"
echo "ADD_SECURITY_HEADERS:    $ADD_SECURITY_HEADERS"
echo "RESTRICT_HTTP_METHODS:   $RESTRICT_HTTP_METHODS"
echo "USE_SITES_ENABLED_CONF:  $USE_SITES_ENABLED_CONF"
echo "ENABLE_INDEX_PHP:        $ENABLE_INDEX_PHP"
echo "SERVER_ADMIN_EMAIL:      $SERVER_ADMIN_EMAIL"
echo "SUBDOMAIN_NAME:          $SUBDOMAIN_NAME"


## check which version of Linux is installed
check_linux_version

## not if on AWS
#if [[ $ADD_SELF_TO_ETC_HOSTS == "true" && AMAZON2_RELEASE == "" ]]; then
if [[ $ADD_SELF_TO_ETC_HOSTS == "true" ]]; then
  addSelfToEtcHostsFile
#else
#  echo "not changing /etc/hosts"
fi

## Get hostname to be substituted in template config files
THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

if [[ "${SUBDOMAIN_NAME}" != "" ]] ; then
  FULLDOMAINNAME="${SUBDOMAIN_NAME}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi

TMPLHOSTNAME="vhost1.virtualrecordlabel.net"
TMPLDOMAINAME="virtualrecordlabel.net"

#TMPLDOMAINAME="${THISDOMAINNAME}"

echo "Apache post-install configuration"
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"
echo "Full Domainname:         $FULLDOMAINNAME"
#echo "Tmpl Host:               $TMPLHOSTNAME"

if [[ $USE_SITES_ENABLED_CONF == "true" ]] ; then
  echo "Apache site-enabled / sites-available"
  DOCROOT="/var/www/html/${FULLDOMAINNAME}/public"

  mkdir /etc/httpd/sites-available
  mkdir /etc/httpd/sites-enabled

  echo "" >> "/etc/httpd/conf/httpd.conf"
  echo "## sites-enabled" >> "/etc/httpd/conf/httpd.conf"
  echo "IncludeOptional sites-enabled/*.conf" >> "/etc/httpd/conf/httpd.conf"

  cd /etc/httpd/sites-enabled/
  ln -s /etc/httpd/sites-available/${FULLDOMAINNAME}.conf /etc/httpd/sites-enabled/${FULLDOMAINNAME}.conf

else
  DOCROOT="/var/www/html/${FULLDOMAINNAME}/public"
fi

## create servername file
echo "Web content root:        ${DOCROOT}"
mkdir -p "${DOCROOT}"

echo "Filling with hostname:   ${DOCROOT}/index.html  and  servername.html"
echo "$THISHOSTNAME" > "${DOCROOT}/index.html"
echo "$THISHOSTNAME" > "${DOCROOT}/servername.html"


echo "Configuring Apache:      /etc/httpd/conf/httpd.conf"
/bin/cp -f "/etc/httpd/conf/httpd.conf" "/etc/httpd/conf/httpd.conf-ORIG"

echo "Setting DocumentRoot:    ${DOCROOT}"

## use Augeas tool to edit conf

if [[ $USE_SITES_ENABLED_CONF == "true" ]] ; then

cat <<EOF | augtool --noautoload
set /augeas/load/Httpd
set /augeas/load/Httpd/lens "Httpd.lns"
set /augeas/load/Httpd/incl "/etc/httpd/conf/httpd.conf"
load
set /files/etc/httpd/conf/httpd.conf/directive[6]/arg "${SERVER_ADMIN_EMAIL}"
save
EOF

else

## set admin email and docroot
cat <<EOF | augtool --noautoload
set /augeas/load/Httpd
set /augeas/load/Httpd/lens "Httpd.lns"
set /augeas/load/Httpd/incl "/etc/httpd/conf/httpd.conf"
load
set /files/etc/httpd/conf/httpd.conf/directive[6]/arg "${SERVER_ADMIN_EMAIL}"
set /files/etc/httpd/conf/httpd.conf/directive[7]/arg "\"${DOCROOT}\""
set /files/etc/httpd/conf/httpd.conf/Directory[3]/arg "\"${DOCROOT}\""
save
EOF

fi

## for PHP enable "index.php"
if [[ $ENABLE_INDEX_PHP == "true" ]] ; then
  echo "ENABLE_INDEX_PHP:        $ENABLE_INDEX_PHP"
  sed -i "s/DirectoryIndex index\.html/DirectoryIndex index.php index.html/" "/etc/httpd/conf/httpd.conf"

## TODO use Augeas
#cat <<EOF | augtool
#set /files/etc/httpd/conf/httpd.conf/Directory[arg='\"${DOCROOT}\"']/*[self::directive='AllowOverride']/arg All
#save
#EOF

fi

## enable AllowOverride in .htaccess files for use by .abba index page styling; also needed for wordpress
cat <<EOF | augtool --noautoload
set /augeas/load/Httpd
set /augeas/load/Httpd/lens "Httpd.lns"
set /augeas/load/Httpd/incl "/etc/httpd/conf/httpd.conf"
load
set /files/etc/httpd/conf/httpd.conf/Directory[arg='\"${DOCROOT}\"']/*[self::directive='AllowOverride']/arg All
save
EOF


echo "ADD_SECURITY_HEADERS     $ADD_SECURITY_HEADERS"

if [[ "$ADD_SECURITY_HEADERS" == "true" ]]; then
  echo "Adding XSS-Protection security headers to httpd.conf"

  echo "" >> "/etc/httpd/conf/httpd.conf"
  echo "## Security headers" >> "/etc/httpd/conf/httpd.conf"
  echo "" >> "/etc/httpd/conf/httpd.conf"

  if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
    echo "Header always append X-Frame-Options SAMEORIGIN" >> "/etc/httpd/conf/httpd.conf"
    echo 'Header set X-XSS-Protection "1; mode=block"' >> "/etc/httpd/conf/httpd.conf"
    echo "Header set X-Content-Type-Options nosniff" >> "/etc/httpd/conf/httpd.conf"

    echo "Header unset ETag" >> "/etc/httpd/conf/httpd.conf"
    echo 'Header set X-Permitted-Cross-Domain-Policies "none"' >> "/etc/httpd/conf/httpd.conf"

    echo "ServerSignature Off" >> "/etc/httpd/conf/httpd.conf"
    echo "TraceEnable Off" >> "/etc/httpd/conf/httpd.conf"
  else
    echo "<IfModule mod_headers.c>" >> "/etc/httpd/conf/httpd.conf"
    echo "  <Directory />" >> "/etc/httpd/conf/httpd.conf"
    echo "    Header always set X-XSS-Protection \"1; mode=block\"" >> "/etc/httpd/conf/httpd.conf"
    echo "    Header always set X-Frame-Options \"SAMEORIGIN\"" >> "/etc/httpd/conf/httpd.conf"
    echo "    Header always set X-Content-Type-Options \"nosniff\"" >> "/etc/httpd/conf/httpd.conf"
    echo "    Header always set Strict-Transport-Security \"max-age=31536000; includeSubDomains\"" >> "/etc/httpd/conf/httpd.conf"
    ##echo "    Header always set Referrer-Policy \"strict-origin\"" >> "/etc/httpd/conf/httpd.conf"
    echo "  </Directory>" >> "/etc/httpd/conf/httpd.conf"
    echo "</IfModule>" >> "/etc/httpd/conf/httpd.conf"

    #echo "Header always append X-Frame-Options SAMEORIGIN" >> "/etc/httpd/conf/httpd.conf"
    #echo 'Header set X-XSS-Protection "1; mode=block"' >> "/etc/httpd/conf/httpd.conf"
    #echo "Header set X-Content-Type-Options nosniff" >> "/etc/httpd/conf/httpd.conf"
    #echo "Header unset ETag" >> "/etc/httpd/conf/httpd.conf"
    #echo 'Header set X-Permitted-Cross-Domain-Policies "none"' >> "/etc/httpd/conf/httpd.conf"
    #echo "ServerSignature Off" >> "/etc/httpd/conf/httpd.conf"
    #echo "TraceEnable Off" >> "/etc/httpd/conf/httpd.conf"
  fi

  echo "" >> "/etc/httpd/conf/httpd.conf"
fi

##echo "ServerTokens Prod" >> "/etc/httpd/conf/httpd.conf"
##echo "FileETag None" >> "/etc/httpd/conf/httpd.conf"
##
##   Header set Content-Security-Policy "default-src 'self';"
##   Header set X-Permitted-Cross-Domain-Policies "none"

HTTPD_CONF_SRC="/usr/local/pbase-data/pbase-apache/etc-httpd-conf-d"
if [[ "${SUBDOMAIN_NAME}" != "" ]] ; then
  HTTPD_CONF_SRC="/usr/local/pbase-data/pbase-apache/etc-httpd-conf-d-subdomain"
fi


if [[ $USE_SITES_ENABLED_CONF == "true" ]] ; then
  /bin/cp -f "${HTTPD_CONF_SRC}/virtualrecordlabel.net.conf" "/etc/httpd/sites-available/${FULLDOMAINNAME}.conf"

  echo "    Virtual host:        /etc/httpd/sites-available/${FULLDOMAINNAME}.conf"
  sed -i "s/virtualrecordlabel.net/${FULLDOMAINNAME}/g" "/etc/httpd/sites-available/${FULLDOMAINNAME}.conf"
else
  echo "    Virtual host:        /etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  /bin/cp -f "${HTTPD_CONF_SRC}/virtualrecordlabel.net.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  sed -i "s/virtualrecordlabel.net/${FULLDOMAINNAME}/g" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
fi

if [[ $RESTRICT_HTTP_METHODS == "true" ]] ; then
  echo "Adding Restrict HTTP Methods directives to httpd.conf"
  echo "" >> "/etc/httpd/conf/httpd.conf"
  echo "## Restrict HTTP Methods" >> "/etc/httpd/conf/httpd.conf"
  echo "" >> "/etc/httpd/conf/httpd.conf"

  echo "RewriteEngine on" >> "/etc/httpd/conf/httpd.conf"
  echo "RewriteCond %{REQUEST_METHOD} ^(CONNECT|TRACE|TRACK|OPTIONS)" >> "/etc/httpd/conf/httpd.conf"
  echo "RewriteRule .* - [R=405,L]" >> "/etc/httpd/conf/httpd.conf"

  echo "" >> "/etc/httpd/conf/httpd.conf"
fi


# Enable httpd service at boot-time, and start httpd service
echo "Enabling service:        httpd"

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig httpd --level 345 on || fail "chkconfig failed to enable httpd service"
  /sbin/service httpd restart || fail "failed to restart httpd service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl enable httpd.service || fail "systemctl failed to enable httpd service"
  /bin/systemctl restart httpd || fail "failed to restart httpd service"
fi

## Add aliases helpful for admin tasks to .bashrc
echo "" >> /root/.bashrc
append_bashrc_alias tailhttp "tail -f /var/log/httpd/error_log /var/log/httpd/access_log"
append_bashrc_alias tailhttpd "tail -f /var/log/httpd/error_log /var/log/httpd/access_log"
append_bashrc_alias tailhttpderr "tail -f -n100 /var/log/httpd/error_log"
append_bashrc_alias tailhttpdaccess "tail -f -n100 /var/log/httpd/access_log"

if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
  append_bashrc_alias stophttpd "service httpd stop"
  append_bashrc_alias starthttpd "service httpd start"
  append_bashrc_alias statushttpd "service httpd status"
  append_bashrc_alias restarthttpd "service httpd restart"
else
  append_bashrc_alias stophttpd "/bin/systemctl stop httpd"
  append_bashrc_alias starthttpd "/bin/systemctl start httpd"
  append_bashrc_alias statushttpd "/bin/systemctl status httpd"
  append_bashrc_alias restarthttpd "/bin/systemctl restart httpd"
fi

WEBSITE_URL="http://${FULLDOMAINNAME}"
echo "Website URL:             ${WEBSITE_URL}"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-apache/el6/etc-httpd-conf/httpd.conf
/usr/local/pbase-data/pbase-apache/el7/etc-httpd-conf/httpd.conf
/usr/local/pbase-data/pbase-apache/fedora/etc-httpd-conf/httpd.conf
/usr/local/pbase-data/pbase-apache/etc-httpd-conf-d/virtualrecordlabel.net.conf
/usr/local/pbase-data/pbase-apache/etc-httpd-conf-d-subdomain/virtualrecordlabel.net.conf