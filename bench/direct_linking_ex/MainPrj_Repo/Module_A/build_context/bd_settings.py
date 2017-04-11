# -*- coding: utf-8 -*- 
import shutil
import copy
import subprocess
import os

def Get_Module_ID():
    return [ 'Module_A','MainPrj_Repo']

def Get_Module_Name() :
    Module_ID=Get_Module_ID()
    module_name = Module_ID[0]
    return module_name

    ##
    # @brief Get dependency info, for each dependency module 
    #         has the configuration connection info. Without 
    #         configuration info, the default connection is 
    #         connected to same configurations
    #
    # @return info of the dependency info
def Get_dependency_module_info(): 
    return [
                [
                  #  ['Module_B','MainPrj_Repo'],
                  #  {
                  #      'x64_Linux_ubuntu':'x64_Linux_ubuntu',
                  #      'x64_Windows':'x64_Windows',
                  #      'arm_Android':'arm_Android',
                  #  }
                ],
                
           ]


def Get_common_bd_env(): 
    return  [
                ['inc_path', ['inc','libsrc','src'] ], 
                ['lib_path', ['lib'] ],            
                ['lib'     , ['pthread' ] ], 
                ['lib_src' , ['libsrc/*.cpp'] ], 
                ['cppflags', [ ] ],
                ['cflags'  , [ ] ],
                ['ccflags' , [ ] ],
            ]                  
 
# Total Build Environment
g_Bd_Environment = [
            ['x64_Linux_ubuntu',
               [
                  ['inc_path',[ ] ],
                  ['lib_path',[ ] ],
                  ['lib'     ,[ ] ],
                  ['lib_src' ,[ ] ],
                  ['src'     ,['src/main.cpp'] ],
                #  ['lib_type' ,'Static' ],
                  ['lib_type' ,'Shared' ],
                  ['swit_src' ,['testframework/swit/*.cpp'] ], 
                  ['swut_src' ,['testframework/swut/*.cpp'] ], 
                  ['test_lib' ,['gtest'] ], 
                  ['test_inc_path' ,['/home/t0/gtest/googletest/include'] ], 
                  ['test_lib_path' ,['/home/t0/gtest/googletest/mybuild'] ], 
                  #['target_lib_name' ,'customized_lib_name' ], # use this to change the library name
               ],
            ],
            ['x64_Windows',
               [
                  [ 'inc_path',[ ] ],
                  [ 'lib_path',[ ] ],
                  [ 'lib'     ,[ ] ],
                  [ 'lib_src' ,[ ] ],
                  [ 'src'     ,['src/main.cpp'] ],
                  [ 'lib_type' ,'Shared' ],
               ],
            ],
            ['arm_Android',
               [
                  [ 'inc_path',[ ] ],
                  [ 'lib_path',[ ] ],
                  [ 'lib'     ,[ ] ],
                  [ 'lib_src' ,[ ] ],
                  [ 'src'     ,[ ] ],
               ],
            ]
        ]

    ##
    # @brief common config independent from configs (platforms,OS ...)
    #
    # @return common config value
def Get_output_common(): 
    return  [
                [ 'inc_path',['inc'] ],
                [ 'lib',['Module_A'] ],
            ]

    ##
    # @brief Get output list 
    #
    # @return Get output list of the module
def Get_output_specific():
    return [
            ['x64_Linux_ubuntu',
                [
                    [ 'inc_path',['inc/x64_Linux_ubuntu'] ],
                    [ 'bin_file',['out/x64_Linux_ubuntu/lib/libModule_A.so'] ],
                    [ 'lib_path',['out/x64_Linux_ubuntu/lib'] ],
                ]
            ],
            ['x64_Windows', 
                [
                    [ 'inc_path',['inc/x64_Windows'] ],
                    [ 'bin_file',['out/x64_Windows/lib/Module_A.dll'] ],
                    [ 'lib_path',['out/x64_Windows/lib'] ],
                ]

            ]

        ]

def Get_output_dirs():
    return [
        'res',
        'lib',
        'bin',
        'doc',
        ]

def Get_Bd_Environment():
    global g_Bd_Environment 
    return g_Bd_Environment
 
def Set_Bd_Environment(val):
    global g_Bd_Environment 
    g_Bd_Environment = copy.deepcopy(val)

def Do_post_build(target_config):
    print("Do post build job")
    #remote_share_dir ="~/01_share/00_web_share"
    #outputdir = 'out/'+target_config+'/'
    #cmd="cp -r "+outputdir+"*"+" "+remote_share_dir
    #print("$ "+cmd)  
    #output=subprocess.call (cmd, shell=True)
    #print("Binary upload done")
