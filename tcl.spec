%define	major	8.6
# temporary workaround for incorrect sonaming previously..
%define	libname	%{mklibname %{name} %{major}}_not0
%define	devname	%mklibname %{name} -d

Summary:	Tool Command Language, pronounced tickle
Name:		tcl
Version:	8.6.0
Release:	%{?pre:0.%{pre}.}2
Group:		System/Libraries
License:	BSD
URL:		http://tcl.tk
Source0:	http://downloads.sourceforge.net/%{name}/%{name}%{version}%{?pre}-src.tar.gz
Source1:	tcl.macros
BuildRequires:	pkgconfig(zlib)
Patch0:		tcl-8.5.10-conf.patch
# From Fedora, replaces old p6 by Stew, rediffed for 8.6 - AdamW 2008/10
Patch2:		tcl-8.6.0-autopath.patch
Patch3:		tcl-8.6.0-fix_includes.patch
Patch4:		tcl-8.6.0-expect-5.43.0.patch
# dead?
#Patch5:		tcl-8.6b1-tdbc_location.patch
Patch6:		tcl-8.6.0-add-missing-linkage-against-libdl.patch
Provides:	/usr/bin/tclsh

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
%patch0 -p1 -b .conf~
%patch2 -p1 -b .autopath~
%patch3 -p1 -b .includes~
%patch4 -p1 -b .expect~
#patch5 -p1 -b .tdbc_location~
%patch6 -p1 -b .ldl_link~
pushd unix
autoconf
popd

%build
pushd unix
    %configure2_5x \
	--enable-threads \
	--enable-64bit \
	--enable-symbols \
	--enable-shared \
	--disable-rpath \
	--includedir=%{_includedir}/tcl%{version}
    %make TCL_LIBRARY=%{_datadir}/%{name}%{major}

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

ln -s libtcl%{major}.so %{buildroot}%{_libdir}/libtcl.so

# and let it be found (we don't look in /usr/lib any more)
ln -s %{_libdir}/%{name}Config.sh %{buildroot}%{_libdir}/%{name}%{major}/%{name}Config.sh

# set up the macros
install -m644 %{SOURCE1} -D %{buildroot}%{_sys_macros_dir}/tcl.macros

# move this crap around
mv %{buildroot}%{_libdir}/%{name}%{major}/tdbc*/libtdbc*.a %{buildroot}%{_libdir}
mv %{buildroot}%{_libdir}/{itcl,sqlite,tdbc,thread}* %{buildroot}%{_libdir}/%{name}%{major}/

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
%{_libdir}/tcl*Config.sh
%{_libdir}/%{name}%{major}/*/*Config.sh
%{_sys_macros_dir}/tcl.macros
%{_libdir}/pkgconfig/*.pc

%changelog
* Sat Jan 12 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 8.6.0-1
- enable regression tests under %%check
- drop dead config script regexp fixes
- place library in a libtcl8.6_not0 package as a temporary workaround for
  previous silly 'libtcl8.6.so.0' soname chosen rather than 'libtcl8.6.so'
- ditch compat headers
- drop ancient lib64 symlink hack
- replace libtcl.so linker script with a simple symlink
- permissions of .so libraries are now handled by spec-helper
- replace soname patch with tcl.m4 patch from fedora (P1, rhbz#81297)
- use pkgconfig() deps for buildrequires
- update summary
- don't explicitly define attributes in %%files
- new version
- merge lost changes from 8.6-0.b2.1 done by bero previously

* Wed Jan  9 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 8.6-0.b1.12
- cleanups
- do autoconf in %%prep

* Tue Apr 26 2011 Paulo Andrade <pcpa@mandriva.com.br> 8.6-0.b1.8mdv2011.0
+ Revision: 659432
- Add zlib-devel to build requires

* Thu Mar 24 2011 Paulo Andrade <pcpa@mandriva.com.br> 8.6-0.b1.7
+ Revision: 648380
- Rebuild

* Mon Jan 24 2011 Paulo Andrade <pcpa@mandriva.com.br> 8.6-0.b1.6
+ Revision: 632487
- Rebuild for newer libxml2

* Mon Dec 06 2010 Jani Välimaa <wally@mandriva.org> 8.6-0.b1.5mdv2011.0
+ Revision: 612610
- add patch to fix buffer overflow with GCC 4.5 -D_FORTIFY_SOURCE=2
  (patch originally from Gentoo)

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 8.6-0.b1.4mdv2011.0
+ Revision: 607983
- rebuild

* Sun Jan 03 2010 Funda Wang <fwang@mandriva.org> 8.6-0.b1.3mdv2010.1
+ Revision: 486057
- Build with thread support

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 8.6-0.b1.2mdv2010.0
+ Revision: 427285
- rebuild

* Wed Dec 24 2008 Adam Williamson <awilliamson@mandriva.org> 8.6-0.b1.1mdv2009.1
+ Revision: 318164
- a few adjustments to accomodate the inclusion of tdbc
- add tdbc_location.patch to install tdbc to the right place
- rediff fix_includes.patch
- new release 8.6b1

* Fri Dec 05 2008 Adam Williamson <awilliamson@mandriva.org> 8.6-0.a3.1mdv2009.1
+ Revision: 310122
- missing prefix/lib on x86-64
- new directory conventions: /usr/share/tcl8.6 (noarch) and /usr/lib/tcl8.6
- disable threaded build (#42596)
- drop libtcl-devel provide (everything should use tcl-devel now)
- drop manual dep on lib (one is auto-generated anyway)
- rediff autopath.patch and don't include /usr/lib in it any more
- add build macros (see policy page, coming soon!, for details)
- add pre-release build conditionals
- new release 8.6a3

* Wed Oct 15 2008 Frederik Himpe <fhimpe@mandriva.org> 8.5.5-1mdv2009.1
+ Revision: 294061
- update to new version 8.5.5

* Fri Aug 15 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.4-1mdv2009.0
+ Revision: 272386
- new release 8.5.4

* Mon Jul 07 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5.3-1mdv2009.0
+ Revision: 232454
- update to new version 8.5.3

* Tue Jun 24 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.2-1mdv2009.0
+ Revision: 228719
- new release 8.5.2

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 8.5.1-3mdv2009.0
+ Revision: 225643
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Mar 18 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.1-2mdv2008.1
+ Revision: 188739
- update autopath.patch from Fedora and also adjust it to include libdir, as we install some tcl modules just in libdir (this was breaking at least tcl-snack, probably others)

* Tue Feb 05 2008 Frederik Himpe <fhimpe@mandriva.org> 8.5.1-1mdv2008.1
+ Revision: 162815
- New upstream bug fix release

* Sat Jan 12 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.0-1mdv2008.1
+ Revision: 149224
- explicitly state 'tcl' in the -devel obsoletes, don't use %%{name}
- replace rpath.patch with a configure option
- rediff expect-5.43.0.patch
- rediff dlopen.patch as per FIXME in spec, replace auto_path.patch with one from Fedora
- rearrange spec to follow MDV norms
- new release 8.5.0 final

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Sep 07 2007 Anssi Hannula <anssi@mandriva.org> 8.5a6-4mdv2008.0
+ Revision: 81976
- own dirs in /usr/lib/tcl8
- rediff and reapply rpath and soname patches

* Wed Jun 20 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a6-3mdv2008.0
+ Revision: 41807
- update url
- handle nicely some stubborn files
- new devel library policy

* Tue Jun 12 2007 Christiaan Welvaart <spturtle@mandriva.org> 8.5a6-2mdv2008.0
+ Revision: 38092
- patch8: export two internal functions for expect

* Thu May 31 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a6-1mdv2008.0
+ Revision: 33182
- new version
- own missing file

* Mon May 21 2007 Jérôme Soyer <saispo@mandriva.org> 8.5a5-6mdv2008.0
+ Revision: 29223
- Bump Release
- Bump Release
- Add Patch for fixing bug #30895

* Mon May 14 2007 Michael Scherer <misc@mandriva.org> 8.5a5-4mdv2008.0
+ Revision: 26605
- fix tcl-devel not installable

* Tue May 08 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a5-3mdv2008.0
+ Revision: 24998
- correct requires
- obsolete tcl8.4

  + Anssi Hannula <anssi@mandriva.org>
    - add conflict for previous version of -devel

* Thu Apr 19 2007 Jérôme Soyer <saispo@mandriva.org> 8.5a5-1mdv2008.0
+ Revision: 15001
- New release 8.5


* Mon Dec 18 2006 Nicolas Lécureuil <neoclust@mandriva.org> 8.4.14-1mdv2007.0
+ Revision: 98570
- Sync sources
- New version 8.4.14
- Import tcl

* Sat Apr 22 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.13-1mdk
- 8.4.13
- drop upstream patches; P5

* Tue Feb 14 2006 Stew Benedict <sbenedict@mandriva.com> 8.4.12-2mdk
- P6: add %%_libdir to $::auto_path on 64bit platforms
  (so addons like tcl-snack will work)

* Tue Feb 14 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.12-1mdk
- 8.4.12
- added P5 from cvs to fix build with bash3.1

* Sun Jan 01 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-6mdk
- fix the tclConfig.sh file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-5mdk
- fix the tclConfig.sh file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-4mdk
- fix the libtcl.so file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-3mdk
- fix soname (P1) after looking at debian
- ship missing headers
- run the test suite
- misc lib64 and spec file fixes

* Thu Dec 29 2005 Guillaume Rousse <guillomovitch@mandriva.org> 8.4.11-2mdk
- first release as a standalone package
- devel files in a devel package
- nuke rpath for real

