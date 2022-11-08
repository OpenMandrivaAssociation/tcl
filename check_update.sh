#!/bin/sh
curl -L https://tcl.tk 2>/dev/null |grep Source |sed -e 's,.*Tcl/Tk ,,;s,<.*,,'
