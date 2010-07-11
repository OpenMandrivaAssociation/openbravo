%define _requires_exceptions pear.Image.Transform.Driver
%define		_mp	MP19
Epoch:		1
Summary:	The WEB-based ERP
Name:		openbravo
Version:	2.50
Release:	%mkrel 7
License:	GPLv3+
Group:		Networking/Other
URL:		http://www.openbravo.com/
Source0:	http://sourceforge.net/projects/openbravo/files/02-openbravo-sources/%{version}%{_mp}/OpenbravoERP-%{version}%{_mp}.tar.bz2
Source1:	Openbravo.properties
Source2:	log4j.lcf
Source3:	http://sourceforge.net/projects/openbravo/files/02-openbravo-sources/%{version}%{_mp}/OpenbravoERP-%{version}%{_mp}.tar.bz2.SHA1
Requires:	tomcat6
Requires:	ant-apache-regexp
Requires:	postgresql-server
Requires:	postgresql
Requires:	postgresql-plpgsql
Suggests:	%{name}-source
BuildRequires:	java-rpmbuild
BuildRequires:	java-1.6.0-openjdk
BuildRequires:	ant
BuildRequires:	ant-apache-regexp
BuildRequires:	postgresql
BuildRequires:	postgresql-server
BuildRequires:	postgresql-plpgsql
BuildRequires:	xerces-j2
BuildRequires:	xml-commons-jaxp-1.3-apis
Conflicts:	ant-antlr
Conflicts:	antlr
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Openbavo's professional web-based open source ERP solution provides a unique
mix of high-impact benefits.

%package        source
Summary:        Openbravo sources
Group:          Networking/Other
Requires:	java-rpmbuild
Requires:	java-1.6.0-openjdk
Requires:	ant
Requires:	ant-apache-regexp
Requires:	postgresql
Requires:	postgresql-server
Requires:	postgresql-plpgsql
Requires:	xerces-j2
Requires:	xml-commons-jaxp-1.3-apis
Suggests:	x11-server-xvfb
Suggests:	tomcat6
Conflicts:	ant-antlr
Conflicts:	antlr

%description    source
Openbavo's professional web-based open source ERP solution provides a unique
mix of high-impact benefits.
This package contains source files needed to add extra modules into 
openbravo.

%prep
%setup -q -n OpenbravoERP-%{version}%{_mp}
%build
rm -rf %{buildroot}

cat > README.mandriva << EOF
Openbravo RPM  for mandriva is split in  to sub-packages:
	openbravo		the already compilled core
	openbravo-source	the class and java source needed to install
				3th party modules

When installing 3th party modules sometimes compillation may fail.  This 
may be because you are missing some of next steps:
	a) tools.jar is missin in CATALINA_HOME/lib
		cp or ln it
		restart tomcat6

	b) X is not accepting connections (your computer has no X running)
		do 
		xhost +
		/usr/bin/Xvfb :1 -screen 0 1024x768x16 &
		export DISPLAY=localhost:1.0
		service tomcat6 restart

	c) Tomcat6 is restarting itself when files change in context
		edit CATALINA_HOME/conf/context.xml
		comment "<WatchedResource>WEB-INF/web.xml</WatchedResource>" 
			line
		restart tomcat6

	d) You are missing some ENV vars
		JAVA_OPTS="-Djava.awt.headless=true -Xms384M -Xmx512M -XX:MaxPermSize=256M"
		the easier way is to add it in /etc/tomcat6/tomcat6.conf
		restart tomcat6

	e) You are mising admin/admin user in tomcat-users.xml
		<user name="admin" password="admin" roles="manager,admin" />	
		retart tomcat6

If you openbravo isntallation complains about compillation errors you may do following:
	a) install -source subpackage and do:
		su tomcat
	b) install -source subpackage and do:
		su tomcat
		cd /usr/src/openbravo
		CATALINA_BASE=/var/lib/tomcat6/ JAVA_HOME=`rpm --eval %java_home` ant war
		CATALINA_BASE=/var/lib/tomcat6/ JAVA_HOME=`rpm --eval %java_home` ant deploy.context
		
Regards//Luis Daniel Lucio Quiroz
dlucio@mandriva.org
EOF
export LC_ALL=C
export PGDATA=/var/tmp/postgresql
export PGPORT=5432
export PGLOG=/var/tmp/pg.log
export LOGFILE=/var/tmp/pg.log
export PGENGINE=/usr/bin
#export CATALINA_BASE=/var/lib/tomcat6/  
export CATALINA_BASE=%{buildroot}/var/lib/tomcat6/
export CLASSPATH=%java_home/lib
%{__mkdir_p} $CATALINA_BASE
export CATALINA_HOME=/usr/share/tomcat6/ 
export JAVA_HOME=%java_home
export JAVA_OPTS="-Djava.awt.headless=true -Xms384M -Xmx512M -XX:MaxPermSize=256M" 
export ANT_OPTS="-Xmx1024M -XX:MaxPermSize=256M"

# Check for the PGDATA structure
	if [ ! -f $PGDATA/PG_VERSION ]
    then
                if [ ! -d $PGDATA ]
		then
			%{__mkdir_p} $PGDATA
			# chown postgres.postgres $PGDATA
			%{__chmod} go-rwx $PGDATA
		fi
		# Initialize the database
		/usr/bin/initdb -U postgres  --pgdata=$PGDATA > /tmp/pg 2>&1
		[ -f $PGDATA/PG_VERSION ] && echo "Init done"
		[ ! -f $PGDATA/PG_VERSION ] && echo "Init failed"
		echo
 	fi

	# Check for postmaster already running...
	# note that pg_ctl only looks at the data structures in PGDATA
	#all systems go -- remove any stale lock files
	RUNPORT=$(netstat -vtnl|grep $PGPORT|wc -l)
	if [ $RUNPORT -eq 0 ] 
	then
		%{__rm} -f /tmp/.s.PGSQL.* > /dev/null
		/usr/bin/pg_ctl -l ${LOGFILE} -D $PGDATA -p /usr/bin/postmaster start  > /dev/null 2>&1
 		sleep 1
	fi

%ant setup
cd config
%ifarch x86_64
./setup-properties-linux-x64.bin  --mode unattended
%else
./setup-properties-linux.bin  --mode unattended
%endif
%{__cp} %{SOURCE1} .
%{__cp} %{SOURCE2} .
#cat Openbravo.properties|sed -r s|bbdd.url=jdbc:postgresql://localhost:5432|bbdd.url=jdbc:postgresql://localhost:$PGPORT| > Openbravo.properties.1
#rm -f Openbravo.properties
#mv Openbravo.properties.1 Openbravo.properties
cd ..
%ant install.source
/usr/bin/vacuumdb -f -z -h '127.0.0.1' -d 'openbravo' -U 'tad'
/usr/bin/pg_dump -U tad -h '127.0.0.1' -F c -b -v -f tad_pgsql.dump openbravo -p $PGPORT

# We dont do diagnostic because tomcat is not running
%{__ln_s} src-util/diagnostic src-diagnostics
%ant war
#%ant diagnostic

# Lets install sources
%{__mkdir_p} %{buildroot}/usr/src/openbravo
%{__cp} -Rv . %{buildroot}/usr/src/openbravo
%{__mkdir_p} %{buildroot}/var/openbravo

# We need to stop temp cluster 
/usr/bin/pg_ctl -m fast -l ${LOGFILE} -D $PGDATA -p /usr/bin/postmaster stop

%pre
/etc/init.d/postgresql restart

%post
export CATALINA_HOME=/usr/share/tomcat6/

# Do this if we are intalling, not  upgrading
if [ $1 = 1 ]; then
	cat > /tmp/create_db.sql << EOF
CREATE ROLE tad LOGIN PASSWORD 'tad' SUPERUSER CREATEDB CREATEROLE VALID UNTIL 'infinity';
UPDATE pg_authid SET rolcatupdate=true WHERE rolname='tad';
CREATE DATABASE openbravo WITH TEMPLATE = template0 ENCODING = 'UTF8' OWNER=tad;
EOF

	echo "Creating DB..."
	/usr/bin/psql -d postgres -U postgres -h 127.0.0.1 -p 5432 -f /tmp/create_db.sql
	echo "Restoring dump..."
	/usr/bin/pg_restore -C -i -U tad -d openbravo -h 127.0.0.1 -p 5432 -O /usr/src/openbravo/tad_pgsql.dump
fi

# Upgrading
if [ $1 = 2 ]; then
	pushd /usr/src/openbravo
	echo "Updating database..."
	%ant update.database
	%ant smartbuild -Dlocal=no
	popd
fi

echo "Vaccuming..."
/usr/bin/vacuumdb -f -z -h '127.0.0.1' -d 'openbravo' -U 'tad'

# Not really sure, because of files sections
/bin/chown tomcat.tomcat /var/lib/tomcat6/webapps/openbravo -Rf

cat /usr/src/openbravo/README.mandriva

%post source
/bin/chown tomcat.tomcat /usr/src/openbravo/ -Rf
/bin/chown tomcat.tomcat /var/openbravo/
/bin/chmod ug+rww /usr/src/openbravo -R

# Workaround for #59560
%ifarch x86_64
if [ !  -f /usr/share/tomcat6/lib/tools.jar ] ; 
	then 
	pushd /usr/share/tomcat6/lib/
	/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0/lib/tools.jar
	ln -s /usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86_64/lib/tools.jar .
	popd
fi
%else
if [ !  -f /usr/share/tomcat6/lib/tools.jar ] ; 
	then 
	pushd /usr/share/tomcat6/lib/
	ln -s /usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0/lib/tools.jar .
	popd
fi
%endif

%clean

%files 
%defattr(-,tomcat,tomcat)
%doc CONTRIBUTORS legal/* tad_pgsql.dump README.mandriva
/var/lib/tomcat6/webapps/*
%dir /var/openbravo

%files source
%defattr(-,tomcat,tomcat)
/usr/src/openbravo/*
/usr/src/openbravo/.classpath
/usr/src/openbravo/.classpath.template
/usr/src/openbravo/.project
/usr/src/openbravo/.settings/org.eclipse.core.resources.prefs
/usr/src/openbravo/.settings/org.eclipse.jdt.core.prefs
/usr/src/openbravo/.settings/org.eclipse.jst.common.project.facet.core.prefs
/usr/src/openbravo/.settings/org.eclipse.wst.common.component
/usr/src/openbravo/.settings/org.eclipse.wst.common.component.template
/usr/src/openbravo/.settings/org.eclipse.wst.common.project.facet.core.xml

