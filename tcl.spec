%define major %(echo %{version} |cut -d. -f1-2)
# temporary workaround for incorrect sonaming previously..
%define libname	%{mklibname %{name} %{major}}_not0
%define devname	%mklibname %{name} -d
%define _disable_lto 1

Summary:	Tool Command Language, pronounced tickle
Name:		tcl
Version:	8.6.8
Release:	1
Group:		System/Libraries
License:	BSD
URL:		http://tcl.tk
Source0:	http://downloads.sourceforge.net/%{name}/%{name}%{version}%{?pre}-src.tar.gz
Source1:	tcl.macros
Source2:	tcl.rpmlintrc
BuildRequires:	pkgconfig(zlib)
Patch0:		tcl-8.6.1-conf.patch
# From Fedora, replaces old p6 by Stew, rediffed for 8.6 - AdamW 2008/10
Patch2:		tcl-8.6.0-autopath.patch
Patch3:		tcl-8.6.1-fix_includes.patch
Patch4:		tcl-8.6.0-expect-5.43.0.patch
# dead?
#Patch5:		tcl-8.6b1-tdbc_location.patch
Patch6:		tcl-8.6.0-add-missing-linkage-against-libdl.patch
Patch7:		tcl-8.4.19-strtod.patch
Provides:	/usr/bin/tclsh
Provides:	tcl(abi) = %{major}

%description
Tcl is a simple scripting language designed to be embedded into
other applications.  Tcl is designed to be used with Tk, a widget
set, which is provided in the tk package.  This package also includes
tclsh, a simple example of a Tcl application.

If you're installing the tcl package and you want to use Tcl for
development, you should also install the tk and tclx packages.

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n %{libname}
Tcl is a simple scripting language designed to be embedded into
other applications.  Tcl is designed to be used with Tk, a widget
set, which is provided in the tk package.  This package also includes
tclsh, a simple example of a Tcl application.

If you're installing the tcl package and you want to use Tcl for
development, you should also install the tk and tclx packages.

%package -n	%{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%mklibname tcl 8.4 -d
Obsoletes:	%mklibname tcl 8.5 -d

%description -n	%{devname}
This package contains development files for %{name}.

%prep
%setup -q -n %{name}%{version}%{?pre}
rm -r compat/zlib
chmod -x generic/tclStrToD.c

%patch0 -p1 -b .conf~
%patch2 -p1 -b .autopath~
%patch3 -p1 -b .includes~
%patch4 -p1 -b .expect~
#patch5 -p1 -b .tdbc_location~
%patch6 -p1
%patch7 -p1 -b .strod
pushd unix
autoconf
popd

%build
export CC=gcc
export CXX=g++
pushd unix
%configure \
    --enable-threads \
    --enable-64bit \
    --enable-symbols \
    --enable-shared \
    --disable-rpath \
    --includedir=%{_includedir}/tcl%{version}

%make CFLAGS="%{optflags}" TCL_LIBRARY=%{_datadir}/%{name}%{major}

popd

%check
make -C unix test

%install
%makeinstall -C unix TCL_LIBRARY=%{buildroot}%{_datadir}/%{name}%{major}

# create the arch-dependent dir
mkdir -p %{buildroot}%{_libdir}/%{name}%{major}

# install all headers
install -d %{buildroot}%{_includedir}/tcl%{version}/generic
install -d %{buildroot}%{_includedir}/tcl%{version}/unix
install -m644 generic/*.h %{buildroot}%{_includedir}/tcl%{version}/generic/
install -m644 unix/*.h %{buildroot}%{_includedir}/tcl%{version}/unix/

pushd %{buildroot}%{_bindir}
    ln -fs tclsh* tclsh
popd

# fix config script, otherwise TCL_SRC_DIR gets wrong value and
# some builds fail because cannot find Tcl private include files
perl -pi -e "s|-L`pwd`/unix\b|-L%{_libdir}|g" %{buildroot}%{_libdir}/tclConfig.sh
perl -pi -e "s|`pwd`/unix/lib|%{_libdir}/lib|g" %{buildroot}%{_libdir}/tclConfig.sh
perl -pi -e "s|`pwd`|%{_includedir}/tcl%{version}|g" %{buildroot}%{_libdir}/tclConfig.sh

ln -s libtcl%{major}.so %{buildroot}%{_libdir}/libtcl.so

# and let it be found (we don't look in /usr/lib any more)
ln -s %{_libdir}/%{name}Config.sh %{buildroot}%{_libdir}/%{name}%{major}/%{name}Config.sh

# set up the macros
install -m644 %{SOURCE1} -D %{buildroot}%{_sys_macros_dir}/tcl.macros

# move this crap around
mv %{buildroot}%{_libdir}/{itcl,sqlite,tdbc,thread}* %{buildroot}%{_libdir}/%{name}%{major}/
# static *stub* libs are needed
mv %{buildroot}%{_libdir}/%{name}%{major}/tdbc*/libtdbc*.a %{buildroot}%{_libdir}

# been unable to track down where this happens for me to patch it properly,
# so let's just manually move it around for now..
mv %{buildroot}%{_libdir}/tcl8/%{major}/* %{buildroot}%{_datadir}/tcl8/%{major}

%files
%{_bindir}/*
%{_datadir}/%{name}%{major}
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_mandir}/mann/*
%{_datadir}/tcl8
%{_libdir}/%{name}%{major}
%exclude %{_libdir}/%{name}%{major}/*/*Config.sh

%files -n %{libname}
%{_libdir}/libtcl%{major}.so

%files -n %{devname}
%dir %{_includedir}/tcl%{version}
%dir %{_includedir}/tcl%{version}/generic
%dir %{_includedir}/tcl%{version}/unix
%{_includedir}/tcl%{version}/generic/*.h
%{_includedir}/tcl%{version}/unix/*.h
%{_includedir}/*.h
%{_libdir}/libtcl.so
%{_libdir}/lib*stub*.a
%{_libdir}/tcl*Config.sh
%{_libdir}/%{name}%{major}/*/*Config.sh
%{_sys_macros_dir}/tcl.macros
%{_libdir}/pkgconfig/*.pc
