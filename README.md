# pbase-rpm-installer
## PBase RPM Installer Application Components
##### Version 1.0

Installing and configuring a Linux server can be challenging. PBase Foundation is a set of configurable RPM installers
that provide a foundation for servers and desktops that work consistently across several versions
of the Red Hat Enterprise Linux and CentOS operating system family.

## Our Almost Famous 3-Minute Installation

Here's how to stand up a WordPress instance on an Apache server with a MySQL database.
```jsx
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-mysql-wordpress
yum -y install pbase-wordpress-allinone
yum -y install pbase-lets-encrypt
```

Additionally, you may want to lock down SSH access and enable the firewall.
```jsx
yum -y install pbase-ssh-fail2ban
## or the 'crowdsec' tool
yum -y install pbase-crowdsec
yum -y install pbase-firewall-enable
```

The goal of the PBase project is to provide base RPM packages for use as starting points for products.
A product-base or "pbase" for short.

Many of the PBase RPMs are configurable with "preconfig" JSON files that override the default settings.
This enables entire application stacks to be configured and installed with ease.


#### PREREQUISITES
Requires a Red Hat EL compatible operating system such as:  
CentOS/RHEL 6, 7 or 8  
Amazon Linux 1 or 2  

#### Check hostname AND domain name

Make sure the target server's `hostname` command returns the fully qualified hostname.
If needed, change it with: 
```
hostnamectl set-hostname myhost1.myrealdomainname.net
```
Also be sure the target server's `hostname -d` command returns the correct domainname.

#### Check /etc/hosts
Be sure the target server's `/etc/hosts` file is correct.
The pbase-preconfig RPM may add a commented-out line with the host's IP and hostname. Enable this line only if needed.
In a DHCP environment your IP address may change on reboot and the value added to /etc/hosts may become stale.
Some of the pbase modules expect the domain name to resolvable.
In these cases that host must either be registered in DNS.


#### Temporarily disable automatic updates
You may want to pause the automatic updates while installing RPMs.  
Do that with the `systemctl stop packagekit` command.

#### Install preconfig RPM
The first step is to install the pbase-preconfig RPM. It places YUM repository specs into the target server's /etc/yum.repos.d/ directory.
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
```
Once that bootstrapping step is done, all the other application components become available.

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
It also lets you choose to permit remote root logins.
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
Depending on your OS version.
To use node version 13, and when using CentOS 8 / EL8
```
yum -y install pbase-preconfig-nodejs13
```
OR to use node version 10 or 12, and when using CentOS 7 / EL7
```
yum -y install pbase-preconfig-nodejs12
yum -y install pbase-preconfig-nodejs10
```
OR to use node version 10, and when using CentOS 6 / EL6
```
yum -y install pbase-preconfig-nodejs10
```
now you can install node and npm with
```  
## CentOS 8
yum -y install --disablerepo=AppStream nodejs

## others
yum -y install nodejs  
```

#### Gatsby JS
#### Build Gatsby JS website
The static site generator Gatsby JS depends on Node JS and a few image procesing libraries to build websites.
Here's how to build from the site's resources and code on a Git repository.  
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-nodejs12
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


#### DOCKER
#### Install Docker CE and Docker Compose
```
yum -y install pbase-preconfig-docker-ce
yum -y install pbase-docker-ce
```


#### KUBERNETES
#### Install Kuberentes and Minikube
```
yum -y install pbase-epel
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
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
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
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-postgres-nextcloud
yum -y install pbase-postgres
yum -y install pbase-nextcloud
```

To install Nextcloud with a MySQL 8.0 community database for storage  
on EL/CentOS 8  
Use these steps:
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-mysql-nextcloud
yum -y --disablerepo=AppStream install mysql-community-server
yum -y install pbase-mysql80community
yum -y install pbase-nextcloud
```
  
on EL/CentOS 6 and 7  
Use these steps:  
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-mysql-nextcloud
yum -y install pbase-mysql80community
yum -y install pbase-nextcloud
```


#### Mattermost

Install the Mattermost messaging platform with a Postgres database for storage  
on CentOS8/EL8
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-postgres-mattermost
yum -y install pbase-postgres
yum -y install pbase-mattermost
yum -y install pbase-lets-encrypt
```

Install the Mattermost messaging platform with a MySQL database for storage  
on CentOS8/EL8
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm 
yum -y install pbase-preconfig-mysql-mattermost
yum -y install pbase-mysql
yum -y install pbase-mattermost
yum -y install pbase-lets-encrypt
```

on CentOS7/EL7  - must use MySQL 8.0 Community release 
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-mysql80community
yum -y install pbase-preconfig-mysql-mattermost
yum -y install pbase-mysql80community
yum -y install pbase-mattermost
yum -y install pbase-lets-encrypt
```

#### GitLab CI/CD UI for git
#### Here's how to stand up a GitLab CE Omnibus stack ready to manage a Git repository.
GitLab is resource hungry and needs at least 4GB of RAM. It also requires CentOS 8.

```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-gitlab-ce
yum -y install pbase-gitlab-ce
```

#### Gitea Lightweight UI for git
#### Here's how to stand up an Apache server with a proxy to a Gitea service ready to manage a Git repository.

Postgres
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-postgres-gitea
yum -y install pbase-postgres
yum -y install pbase-apache
yum -y install pbase-gitea
```

MySQL
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-mysql-gitea
yum -y install pbase-mysql
yum -y install pbase-apache
yum -y install pbase-gitea
```

#### WordPress
#### Here's how to stand up a WordPress instance on an Apache server with a MySQL database.
```
## preconfig
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-mysql-wordpress

## apache and mysql
yum -y install pbase-apache
yum -y install pbase-mysql

## optional - to add content
yum -y install vrl-preconfig
yum -y install vrl-website-content

## wordpress
yum -y install pbase-wordpress
```


#### Desktop IDE
#### VSCode IDE
To install the Microsoft Visual Studio Code - VSCode integrated development environment.
Also to support large projects it will increase the Linux fs.inotify.max_user_watches to 524288.
```
yum -y install pbase-preconfig-vscode-ide
yum -y install code
```

#### IntelliJ/WebStorm IDE
To install the IntelliJ or WebStorm integrated development environment.
Also to support large projects it will increase the Linux fs.inotify.max_user_watches to 524288.
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


A wide variety of media components in the rpm-fusion repository.  
Here's how to install obs-studio:
```
yum -y install pbase-rpmfusion
yum -y install obs-studio
```


#### ActivityPub application stacks

Here's how to install Mastodon:
(Note: On RHEL 8 you must enable CodeReadyBuilder with:  subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms)
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-postgres-mastodon
yum -y install pbase-postgres
yum -y install activpb-mastodon
```

Here's how to install Peertube:
Default install is to assume your domain is registered in DNS with a 'peertube' subdomain.  
For example: peertube.mydomainname.com  
If you want to change this edit the `activpb_peertube.json` preconfig file.
```
yum -y install https://pbase-foundation.com/pbase-preconfig.rpm
yum -y install pbase-preconfig-postgres-peertube
yum -y install pbase-postgres
yum -y install activpb-peertube
```
