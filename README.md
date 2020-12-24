# pbase-rpm-installer
## PBase RPM Installer Application Components
##### Version 1.0

Installing and configuring a Linux server can be challenging. 
PBase-Foundation is a set of configurable RPM installers
that provide a foundation for servers and desktops that work consistently across several versions
of the Red Hat Enterprise Linux and CentOS operating system family.
Several application stack installers are provided using these RPM components.

## Our Almost Famous 3-Minute Installation

Here's how to stand up a WordPress instance on an Apache server with a MySQL database.
```jsx
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql-wordpress
yum -y install pbase-wordpress-allinone
yum -y install pbase-lets-encrypt
```

Additionally, you may want to lock down SSH access and enable the firewall.
```jsx
yum -y install pbase-ssh-fail2ban
yum -y install pbase-firewall-enable
```

The goal of the PBase project is to provide base RPM packages for use as starting points for products.
A product-base or "pbase" for short.

Many of the PBase RPMs are configurable with "preconfig" JSON files that override the default settings.
This enables entire application stacks to be configured and installed with ease.


#### PREREQUISITES
Requires a Red Hat Enterprise Linux (EL) compatible operating system such as:
- Red Hat EL 6, 7 or 8
- CentOS 6, 7, 8 including CentOS Steam 8
- Amazon Linux 1 or 2 AMI
- Fedora 3x (tested on Fedora versions 31 through 33 for most RPM components)

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

#### Install the PBase repository RPM
The first step is to install the pbase-repo RPM. 
It places YUM repository specs into the target server's /etc/yum.repos.d/ directory.
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
```
Once that bootstrapping step is done, all the other pbase application components become available.

#### Install apache standard RPM
```
yum -y install pbase-preconfig-apache
yum -y install pbase-apache
yum -y install pbase-preconfig-lets-encrypt
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
yum -y install pbase-terraform
``` 

Use Terraform to manage your servers and infrastructure.
```
yum -y install pbase-terraform
``` 

## Node JS
#### Install the latest Node JS release
Depending on your OS version select the appropriate preconfig rpm 
to install the NodeSource repository for Node JS version 10, 12 or 14.

EL8/CentOS 8 - requires passing `--disablerepo=AppStream` to point to the NodeSource repo
```  
yum -y install pbase-preconfig-nodejs12
## or
yum -y install pbase-preconfig-nodejs14
yum -y install --disablerepo=AppStream nodejs
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
yum -y install pbase-preconfig-nodejs12
yum -y install nodejs  
yum -y install pbase-gatsby-tools

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
npm install
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
yum -y --disablerepo=AppStream install postgresql11-server postgresql11-contrib
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
yum -y --disablerepo=AppStream install postgresql12-server postgresql12-contrib
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
yum -y --disablerepo=AppStream install postgresql13-server postgresql13-contrib
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
yum -y --disablerepo=AppStream install mysql-community-server
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

#### Nextcloud
  
Install the Nextcloud PHP based application.
Either PostgreSQL or MySQL 8.0 community can be used.  

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
yum -y --disablerepo=AppStream install mysql-community-server
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
yum -y install pbase-apache
yum -y install pbase-gitea
```

MySQL
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-mysql-gitea
yum -y install pbase-mysql
yum -y install pbase-apache
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
Install the EPEL repo first to provide the 'dkms' library.
Then install the pbase-preconfig-virtualbox the package and reboot to activate the VirtualBox environment variables.
Select the host VirtualBox application's menu item: Devices > Insert the Guest Additions CD Image. 
This will bring up the "Run" dialog in the guest.
Follow the prompts to complete the kernel rebuild.
Finally, reboot your VirtualBox guest VM to see the Guest Additions running.
```
yum -y install pbase-epel
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
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install activpb-preconfig-postgres-mastodon
yum -y install pbase-postgres
yum -y install activpb-mastodon
```

Here's how to install Peertube:
Default install is to assume your domain is registered in DNS with a 'peertube' subdomain.  
For example: peertube.mydomainname.com  
If you want to change this edit the `activpb_peertube.json` preconfig file.
```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install activpb-preconfig-postgres-peertube
yum -y install pbase-postgres
yum -y install activpb-peertube
```


#### SOLID NSS: Node Solid Server

```
yum -y install https://pbase-foundation.com/pbase-repo.rpm
yum -y install pbase-preconfig-node-solid-server
yum -y install --enablerepo=AppStream python3
yum -y install --disablerepo=AppStream nodejs
yum -y install pbase-apache
yum -y install pbase-lets-encrypt
yum -y install pbase-node-solid-server
```


