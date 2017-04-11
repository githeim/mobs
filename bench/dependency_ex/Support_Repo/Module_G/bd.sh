#!/bin/bash
#scons -Q --debug=time CONFIG=x64_Linux_ubuntu $*
scons -Q --debug=time CONFIG=x64_Linux_ubuntu TT=304 $*
#scons -Q --debug=time CONFIG=x64_Windows $*
