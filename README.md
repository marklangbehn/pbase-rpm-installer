# pbase-rpm-installer
## PBase RPM Installer Application Components
##### Version 1.0

Installing and configuring a Linux server can be challenging. 
PBase-Foundation is a set of configurable RPM installers
that provide a foundation for servers and desktops that work consistently across several versions
of the operating system family based on Red Hat Enterprise Linux (EL), 
such as CentOS, Alma Linux, Rocky Linux and Oracle Linux.
Several application stack installers are provided using these RPM components.

## Our Almost Famous 4-Minute Installation

Here's how to stand up a WordPress instance on an Apache server with a MySQL database.
In the first command replace the email sample with your appropriate admin email address.
```jsx
echo "pbase.foundation@gmail.com" > /root/DEFAULT_EMAIL_ADDRESS.txt
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql-wordpress
yum -y install pbase-wordpress-allinone
yum -y install pbase-lets-encrypt
```

Additionally, you may want to lock down SSH access and enable the firewall.
```jsx
yum -y install pbase-ssh-fail2ban
yum -y install pbase-preconfig-firewall-enable
yum -y install pbase-firewall-enable
```

The goal of the PBase project is to provide base RPM packages for use as starting points for products.
A product-base or "pbase" for short.

Many of the PBase RPMs are configurable with "preconfig" JSON files that override the default settings.
This enables entire application stacks to be configured and installed with ease.


#### PREREQUISITES
Requires a Red Hat Enterprise Linux (EL) compatible operating system such as:
- Red Hat EL 7, 8 or 9 - including AlmaLinux and Rocky Linux
- Amazon Linux 2 AMI or Amazon Linux 2022
- Fedora 3x (tested on Fedora versions 33 through 36 for most RPM components)

All `yum` install commands must be run as root user, or using sudo.

#### DNS

If your server has its domain name registered in DNS our RPMs can generate a valid HTTPS certificate with Let's Encrypt.
Several of the application stacks assume a valid DNS is ready and will do just that. 

#### Check hostname AND domain name

Make sure the target server's `hostname` command returns the fully qualified hostname.
If needed, change it with the hostnamectl command, substituting your correct value: 
```
hostnamectl set-hostname myhost1.myrealdomainname.net
```
Also be sure the target server's `hostname -d` command returns the correct domainname.

#### Check /etc/hosts
Be sure the target server's `/etc/hosts` file is correct.

#### Temporarily disable automatic updates
You may want to pause the automatic updates while installing RPMs.  
On some systems you can do that with the `systemctl stop packagekit` command.

#### Set default email address file, and install the PBase repository RPM
First create a text file containing your admin email address in the /root directory called `DEFAULT_EMAIL_ADDRESS.txt`
similarly, some rpms use DEFAULT_DESKTOP_USERNAME and DEFAULT_SUB_DOMAIN files to provide defaults.
 ... then install the pbase-repo RPM.
It places YUM repository specs into the target server's /etc/yum.repos.d/ directory.
```
echo "pbase.foundation@gmail.com" > /root/DEFAULT_EMAIL_ADDRESS.txt
echo "mark" > /root/DEFAULT_DESKTOP_USERNAME.txt
echo "app" > /root/DEFAULT_SUB_DOMAIN.txt
echo "000myrealoutgoingsmtppassword999" > /root/DEFAULT_SMTP_PASSWORD.txt

yum -y install https://pbase-foundation.com/pbase-repo.rpm
```
Once that bootstrapping step is done, all the other pbase application components become available.

#### Install apache standard RPM
```
yum -y install pbase-preconfig-apache
yum -y install pbase-preconfig-firewall-enable
yum -y install pbase-apache
yum -y install pbase-lets-encrypt
yum -y install pbase-firewall-enable
```

#### How to watch Apache server logs
When install is done, load the shell-aliases from /root/.bashrc and run the "tailhttpd" alias.
```
source ~/.bashrc
tailhttpd
```

#### SSH Fail2Ban or SSH Alternate Port 

For sophisticated access monitoring of SSH login attempts use Fail2Ban.
It requires that firewalld service be installed and enabled.
```
yum -y install pbase-preconfig-firewall-enable
yum -y install pbase-firewall-enable
yum -y install pbase-preconfig-ssh-fail2ban
yum -y install pbase-ssh-fail2ban
``` 

Or to simply configure SSH to listen on a port other than 22 use the pbase-ssh-port package. 
The preconfig package lets you choose the alternate SSH port number which defaults 29900.
And whether permit remote root logins, which it disables by default.
```
yum -y install pbase-preconfig-ssh-port
yum -y install pbase-ssh-port
``` 

#### Hashicorp Terraform and Vault
Use Vault to securely manage your configuration and secrets.
```
yum -y install pbase-preconfig-vault
yum -y install pbase-vault
``` 

Use Terraform to manage your servers and infrastructure.
```
yum -y install pbase-preconfig-terraform
yum -y install pbase-terraform
``` 

## Node JS
#### Install the latest Node JS release
Depending on your OS version select the appropriate preconfig rpm 
to install the NodeSource repository for Node JS version 10, 12 or 14.

EL8/CentOS 8 - requires passing `--disablerepo=appstream` to point to the NodeSource repo
```
yum -y install pbase-preconfig-yarn

yum -y install pbase-preconfig-nodejs12
## or
yum -y install pbase-preconfig-nodejs14
yum -y install --enablerepo=appstream python3
yum -y install --disablerepo=appstream nodejs
yum -y install yarn
```

EL7/CentOS 7
```  
yum -y install pbase-preconfig-nodejs10
## or
yum -y install pbase-preconfig-nodejs12
## or
yum -y install pbase-preconfig-nodejs14
yum -y install nodejs  
```

EL6/CentOS 6
```  
yum -y install pbase-preconfig-nodejs10
## or
yum -y install pbase-preconfig-nodejs12
yum -y install nodejs  
```

Fedora 3x - to override the built-in Node JS version 14.
```  
yum -y install pbase-preconfig-nodejs12
## or
yum -y install pbase-preconfig-nodejs14

## check the exact version available with yum provides 
## for example installing version 12:
yum provides nodejs
yum -y install nodejs-12.19
```

#### Gatsby JS
#### Build Gatsby JS website
The static site generator Gatsby JS depends on Node JS and a few image procesing libraries to build websites.
Here's how to build from the site's resources and code on a Git repository.
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-nodejs14

## if on CentOS 8 Stream
yum -y install --enablerepo=appstream python3
yum -y install --disablerepo=appstream nodejs

## other EL version
yum -y install nodejs

yum -y install pbase-gatsby-tools
yum -y install yarn
```

As a regular user, create a file `~/.netrc` and fill it with your Git source info.
```
machine gitlab.com
login myrealgitusername
password myReAlPaSsWoRd
```
Then clone the website source, and build it.
```
git clone https://gitlab.com/mlangbehn/emosonic-site.git
cd emosonic-site
yarn
gatsby build
```
Finally, copy the `public` directory that was built to your website root.


#### POSTGRES

Postgres - using the default repo 
```
yum -y install pbase-preconfig-postgres
yum -y install pbase-postgres
```
Postgres 11 - using the postgresql.org repo
```
yum -y install pbase-preconfig-postgres11
yum -y install pbase-postgres11
```

Postgres 11 - using the postgresql.org repo - on CentOS 8 only  
```
yum -y install pbase-preconfig-postgres11
yum -y --disablerepo=appstream install postgresql11-server postgresql11-contrib
yum -y install pbase-postgres11
```


Postgres 12 - using the postgresql.org repo
```
yum -y install pbase-preconfig-postgres12
yum -y install pbase-postgres12
```

Postgres 12 - using the postgresql.org repo - on CentOS 8 only  
```
yum -y install pbase-preconfig-postgres12
yum -y --disablerepo=appstream install postgresql12-server postgresql12-contrib
yum -y install pbase-postgres12
```



Postgres 13 - using the postgresql.org repo
```
yum -y install pbase-preconfig-postgres13
yum -y install pbase-postgres13
```

Postgres 13 - using the postgresql.org repo - on CentOS 8 only  
```
yum -y install pbase-preconfig-postgres13
yum -y --disablerepo=appstream install postgresql13-server postgresql13-contrib
yum -y install pbase-postgres13
```


## MySQL
MYSQL - using the default repo
```
yum -y install pbase-preconfig-mysql
yum -y install pbase-mysql
```

MYSQL 8.0 - using the MySQL Community repo
```
yum -y install pbase-preconfig-mysql80community
yum -y install pbase-mysql80community
```

MYSQL 8.0 - using the MySQL Community repo - on CentOS 8 only
```
yum -y install pbase-preconfig-mysql80community
yum -y --disablerepo=appstream install mysql-community-server
yum -y install pbase-mysql80community
```

The Adminer database Web UI
```
yum -y install pbase-adminer
```


#### MONGODB.ORG
#### Install MongoDB Community Server edition from mongodb.org
```
yum -y install pbase-preconfig-mongodb-org
yum -y install pbase-mongodb-org
```


#### DOCKER
#### Install Docker CE and Docker Compose
```
yum -y install pbase-preconfig-docker-ce
yum -y install pbase-docker-ce
```


#### KUBERNETES
#### Install Kuberentes and Minikube
```
yum -y install pbase-kvm
yum -y install pbase-kubernetes-tools
```

Here's some example commands of setting up the Portainer UI with docker.
```
docker pull portainer/portainer
docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer

docker pull centos
docker run -it centos
```


#### JAVA
#### Check for existing Java version if needed
You may need to remove an existing version of Java. Here's an example of removing Java 1.7 and 1.8.
```
yum remove java*
yum remove java-1.7.0-openjdk*
yum remove java-1.8.0-openjdk*
```

Only if needed, choose your version of Java.  
Here's commands to install either version 1.8 or 11.
```
yum -y install java-1.8.0-openjdk-devel  
OR
yum -y install java-11-openjdk-devel
```
to get Java along with Maven and other developer command line tools
```
yum -y install pbase-java8-dev-tools
OR
yum -y install pbase-java11-dev-tools
```

Tomcat 8 Install and start service
```
yum -y install pbase-tomcat8
```

#### ELASTICSEARCH
To install and start the elasticsearch service. Must have the Java 1.8 JRE already installed before installing the elasticsearch package.
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install java-1.8.0-openjdk
yum -y install pbase-preconfig-elasticsearch
yum -y install pbase-elasticsearch
```
(You may need to reboot to let the elasticsearch service start correctly.)  
When install is done load the shell-aliases from .bashrc and run the "tailelastic" alias.
```
source ~/.bashrc
tailelastic
```

#### PHP 7.4
The Remi PHP repository is installed first with the remi-release-XX.rpm file URL whose name matches to your OS.
Then depending on your OS version a pair of yum commands will be needed to enable the php from the Remi repo.  
  
Start with installing the pbase-repo ...
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
```

EL8 - add remi repo
```
yum -y install pbase-epel
yum -y install https://rpms.remirepo.net/enterprise/remi-release-8.rpm
yum -y module reset php
yum -y module install php:remi-7.4
```

EL7 - add remi repo
```
yum -y install pbase-epel
yum -y install https://rpms.remirepo.net/enterprise/remi-release-7.rpm
yum -y install yum-utils
yum-config-manager --enable remi-php74
yum install php
```

FEDORA 34 - add remi repo
```
yum -y install https://rpms.remirepo.net/fedora/remi-release-34.rpm
yum -y module reset php
yum -y module install php:remi-7.4
```

Amazon Linux 2
```
amazon-linux-extras install php7.4
```


#### Nextcloud
  
Install the Nextcloud PHP based application.
Either PostgreSQL or MySQL 8.0 community can be used.  
First create the default email text file.  
`echo "pbase.foundation@gmail.com" > /root/DEFAULT_EMAIL_ADDRESS.txt`
`echo "nextcloud" > /root/DEFAULT_SUB_DOMAIN.txt`

To install Nextcloud with a Postgres database for storage  
Use these steps:  
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-postgres-nextcloud
yum -y install pbase-postgres
yum -y install pbase-nextcloud
```

To install Nextcloud with a MySQL 8.0 community database for storage  
on EL/CentOS 8  
Use these steps:
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql-nextcloud
yum -y --disablerepo=appstream install mysql-community-server
yum -y install pbase-mysql80community
yum -y install pbase-nextcloud
```
  
on EL/CentOS 6 and 7  
Use these steps:  
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql-nextcloud
yum -y install pbase-mysql80community
yum -y install pbase-nextcloud
```


#### Mattermost

Install the Mattermost messaging platform with a Postgres database for storage  
on CentOS8/EL8

```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-postgres-mattermost
yum -y install pbase-postgres
yum -y install pbase-mattermost
yum -y install pbase-lets-encrypt
```

Install the Mattermost messaging platform with a MySQL database for storage  
on CentOS8/EL8
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm 
yum -y install pbase-preconfig-mysql-mattermost
yum -y install pbase-mysql
yum -y install pbase-mattermost
yum -y install pbase-lets-encrypt
```

on CentOS7/EL7  - must use MySQL 8.0 Community release 
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql80community
yum -y install pbase-preconfig-mysql-mattermost
yum -y install pbase-mysql80community
yum -y install pbase-mattermost
yum -y install pbase-lets-encrypt
```

#### GitLab CI/CD UI for git
#### Here's how to stand up a GitLab CE Omnibus stack ready to manage a Git repository.
GitLab is resource hungry and needs more than 4GB of available RAM. It also requires CentOS 8.

```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-gitlab-ce
yum -y install pbase-gitlab-ce
```

#### Gitea Lightweight UI for git
#### Here's how to stand up an Apache server with a proxy to a Gitea service ready to manage a Git repository.

Postgres
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-postgres-gitea
yum -y install pbase-postgres
yum -y install pbase-gitea
```

MySQL
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql-gitea
yum -y install pbase-mysql
yum -y install pbase-gitea
```

#### WordPress
#### Here's how to stand up a WordPress instance on an Apache server with a MySQL database.
```
## preconfig
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql-wordpress

## apache and mysql
yum -y install pbase-apache
yum -y install pbase-mysql

## optional - to add content
yum -y install vrl-repo
yum -y install vrl-website-content

## wordpress
yum -y install pbase-wordpress
```


#### Desktop IDE
#### VSCode IDE
To install the Microsoft Visual Studio Code - VSCode integrated development environment.
Also to support large projects it will increase the Linux kernel parameter fs.inotify.max_user_watches to 524288.
```
yum -y install pbase-preconfig-vscode-ide
yum -y install code
```

#### IntelliJ/WebStorm IDE
To install the IntelliJ IDEA Community Edition, or the WebStorm integrated development environment.
Also to support large projects it will increase the Linux kernel parameter fs.inotify.max_user_watches to 524288.
```
yum -y install pbase-jetbrains-intellij-ide
yum -y install pbase-jetbrains-webstorm-ide
```


## Chrome

Use this if you want to add the Google Chrome yum repo.
```
yum -y install pbase-preconfig-chrome
yum -y install google-chrome-stable
```

#### Other component RPMs are available
  
```
yum -y install pbase-preconfig-timesync-enable
yum -y install pbase-timesync-enable
```

#### VirtualBox dependencies
Then install the pbase-preconfig-virtualbox the package and reboot to activate the VirtualBox environment variables.
Select the host VirtualBox application's menu item: Devices > Insert the Guest Additions CD Image. 
This will bring up the "Run" dialog in the guest.
Follow the prompts to complete the kernel rebuild.
Finally, reboot your VirtualBox guest VM to see the Guest Additions running.
```
yum -y install pbase-preconfig-virtualbox
```

#### CentOS 8 Stream only - realtime kernel
  
```
yum -y install pbase-preconfig-realtime-kernel
yum -y install pbase-realtime-kernel
```

#### RPMFusion

A wide variety of media applications and components are available in the rpm-fusion repository.  
First install the main pbase-rpmfusion package. Once that is installed you can enable 
additional packages that include more codecs as shown below.
```
yum -y install pbase-rpmfusion
yum -y install rpmfusion-free-release-tainted
yum -y install rpmfusion-nonfree-release-tainted
yum -y groupinstall multimedia
```

Once those codecs and dependencies are enabled you
can install a DVD player and obs-studio:
```
yum -y install libdvdcss
yum -y install vlc
yum -y install obs-studio
```


#### ActivityPub application stacks

Here's how to install Mastodon:
(Note: On RHEL 8 you must enable CodeReadyBuilder with:  subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms)

Mastodon requires Node JS 16 or higher:
```
curl -sL https://rpm.nodesource.com/setup_16.x | bash -
yum -y install gcc-c++ make
yum -y install nodejs
```

After Node JS is installed you are ready to install Mastodon
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install activpb-preconfig-postgres-mastodon
yum -y install pbase-postgres
yum -y install activpb-mastodon
```

Here's how to install Peertube:
The default install assumes your domain is registered in DNS with a 'peertube' subdomain.  
For example: peertube.mydomainname.com  
If you want to change this edit the `activpb_peertube.json` preconfig file.

Requires Node JS 14 or higher:
```
curl -sL https://rpm.nodesource.com/setup_14.x | bash -
yum -y install nodejs
```
After Node JS is installed you are ready to install Peertube
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install activpb-preconfig-postgres-peertube
yum -y install pbase-postgres
yum -y install activpb-peertube
```

#### GoTTY
#### Terminal shell webapp - gotty
The gotty service is written in Go and implements a webpage for a terminal login shell.
```
echo "pbase.foundation@gmail.com" > /root/DEFAULT_EMAIL_ADDRESS.txt
echo "shell" > /root/DEFAULT_SUB_DOMAIN.txt
echo "mark" > /root/DEFAULT_DESKTOP_USERNAME.txt
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-gotty
yum -y install pbase-golang-tools
yum -y install pbase-gotty
```

