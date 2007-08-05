# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'
%define _without_maven 1
%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define section     free

Name:           plexus-velocity
Version:        1.1.6
Release:        %mkrel 0.0.1
Epoch:          0
Summary:        Plexus Velocity Component
License:        MIT
Group:          Development/Java
URL:            http://plexus.codehaus.org/
# svn export http://svn.codehaus.org/plexus/plexus-components/tags/plexus-velocity-1.1.6/ && tar cvvjf plexus-velocity-1.1.6.tar.bz2 plexus-velocity-1.1.6/
Source0:        plexus-velocity-%{version}.tar.bz2
Source1:        plexus-velocity-1.1.6-build.xml
Source2:        plexus-velocity-1.1.6-project.xml

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRequires:  ant >= 0:1.6
BuildRequires:  jpackage-utils >= 0:1.6
%if %{with_maven}
BuildRequires:  maven >= 0:1.1
%endif
BuildRequires:  ant-nodeps
BuildRequires:  classworlds >= 0:1.1
BuildRequires:  jakarta-commons-collections
BuildRequires:  jakarta-commons-logging
BuildRequires:  plexus-container-default
BuildRequires:  plexus-utils
BuildRequires:  velocity
Requires:  classworlds >= 0:1.1
Requires:  jakarta-commons-collections
Requires:  plexus-container-default
Requires:  plexus-utils
Requires:  velocity

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
Requires(post):         java-gcj-compat
Requires(postun):       java-gcj-compat
%endif

%description
The Plexus project seeks to create end-to-end developer tools for
writing applications. At the core is the container, which can be
embedded or for a full scale application server. There are many
reusable components for hibernate, form processing, jndi, i18n,
velocity, etc. Plexus also includes an application server which
is like a J2EE application server, without all the baggage.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%prep
%setup -q
for j in $(find . -name "*.jar"); do
        rm $j
done
cp %{SOURCE1} build.xml
cp %{SOURCE2} project.xml

%build
%if %{with_maven}
#mkdir -p .maven/repository/maven/jars
#build-jar-repository .maven/repository/maven/jars \
#maven-jelly-tags

#mkdir -p .maven/repository/JPP/jars
#build-jar-repository -s -p .maven/repository/JPP/jars \
#classworlds \
#commons-collections \
#commons-logging-api \
#plexus/container-default \
#plexus/utils \
#velocity \

export MAVEN_HOME_LOCAL=$(pwd)/.maven
maven \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=$MAVEN_HOME_LOCAL \
        jar:install javadoc

%else

mkdir -p target/lib
build-jar-repository -s -p target/lib \
classworlds \
commons-collections \
commons-logging-api \
plexus/container-default \
plexus/utils \
velocity \

%{ant} jar javadoc

%endif

%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/plexus
install -pm 644 target/%{name}-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/plexus/velocity-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir}/plexus && for jar in *-%{version}*; \
do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root,-)
%{_javadir}/*

%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/velocity-%{version}.jar.*
%endif

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/*
