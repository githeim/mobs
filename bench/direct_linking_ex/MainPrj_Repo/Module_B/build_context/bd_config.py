# -*- coding: utf-8 -*- 
import os

DEFAULT_CONFIG = 'x64_Linux_ubuntu'
CONFIG_DIC ={
    'x64_Linux_ubuntu':{
        'PATH':     '/usr/bin'+':'+str(os.environ['PATH']),
        'CC':       'gcc',
        'CXX':      'g++',
        'CPP':      'gcc',
        'AS':       'as',
        'LD':       'ld',
        'GDB':      'gdb',
        'STRIP':    'strip',
        'RANLIB':   'ranlib',
        'OBJCOPY':   'objcopy',
        'OBJDUMP':   'objdump',
        'AR':       'ar',
        'NM':       'nm',
        'CFLAGS':   ['',],
        'CXXFLAGS':   ['',],
        'SHLIBSUFFIX':'.so',
        'SHLIBPREFIX':'lib',     
        'PROGSUFFIX':'',
        'LINKFLAGS':['-pthread'],
    },
    'x64_Windows':{
        'PATH':     '/opt/mingw64/bin'+':'+str(os.environ['PATH']),
        'CC':       'x86_64-w64-mingw32-gcc',
        'CXX':      'x86_64-w64-mingw32-g++',
        'CPP':      'x86_64-w64-mingw32-gcc',
        'AS':       'x86_64-w64-mingw32-as',
        'LD':       'x86_64-w64-mingw32-ld',
        'GDB':      'x86_64-w64-mingw32-gdb',
        'STRIP':    'x86_64-w64-mingw32-strip',
        'RANLIB':   'x86_64-w64-mingw32-ranlib',
        'OBJCOPY':  'x86_64-w64-mingw32-objcopy',
        'OBJDUMP':  'x86_64-w64-mingw32-objdump',
        'AR':       'x86_64-w64-mingw32-ar',
        'NM':       'x86_64-w64-mingw32-nm',
        'CFLAGS':   [''],
        'CXXFLAGS':   ['',],
        'SHLIBSUFFIX':'.dll', # for Windows DLL
        'SHLIBPREFIX':'',      # for Windows DLL
        'SHCCFLAGS':'', #in Windows -fPIC option isn't needed
        'PROGSUFFIX':'.exe',
        'LINKFLAGS':['-static-libgcc', '-static-libstdc++'],
    },
    'arm_Android':{
    },
}
