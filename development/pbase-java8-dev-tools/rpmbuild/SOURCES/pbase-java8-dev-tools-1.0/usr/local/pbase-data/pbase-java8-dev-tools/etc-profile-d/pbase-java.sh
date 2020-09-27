JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:/bin/java::")
export JAVA_HOME

PATH=$JAVA_HOME/bin:$PATH
export PATH
