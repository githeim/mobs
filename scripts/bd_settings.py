# -*- coding: utf-8 -*- 
import shutil
import copy
import subprocess
import os

def Get_Module_ID():
    return [ 'D_E_L_I_getPrjName_','D_E_L_I_getGroupName_']

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
              # Example
              #  [
              #      ['SDL2','SupportLayer'],
              #      {
              #          'x64_Linux_ubuntu':'x64_Linux_ubuntu',
              #          'x64_Windows':'x64_Windows',
              #          'arm_Android':'arm_Android',
              #      }
              #  ],
              #  [
              #      ['SDL2_ttf','SupportLayer'],
              #      {
              #          'x64_Linux_ubuntu':'x64_Linux_ubuntu',
              #          'x64_Windows':'x64_Windows',
              #          'arm_Android':'arm_Android',
              #      }
              #  ]

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
def Get_specific_bd_env():   
  return [
            ['x64_Linux_ubuntu',
               [
                  ['inc_path',[ ] ],
                  ['lib_path',['out/x64_Linux_ubuntu/lib' ] ],
                  ['lib'     ,[ ] ],
                  ['lib_src' ,[ ] ],
                  ['src'     ,['src/main.cpp'] ],
                  ['lib_type' ,'Shared' ],
                  ['swit_src' ,['testframework/swit/*.cpp'] ], 
                  ['swut_src' ,['testframework/swut/*.cpp'] ], 
                  ['test_lib' ,['gtest'] ], 
                  ['test_inc_path' ,['D_E_L_I_getTestFramework_Path_/include'] ], 
                  ['test_lib_path' ,['D_E_L_I_getTestFramework_Path_/mybuild'] ], 
                  #['target_lib_name' ,'customized_lib_name' ], # use this to change the library name
                  ['direct_linking','False'], 
                  # --> if you want to use the libsrc codes in src code level
                  #     use this option , default ; 'False'
               ],
            ],
            ['x64_Windows',
               [
                  [ 'inc_path',[ ] ],
                  [ 'lib_path',['out/x64_Windows/lib' ] ],
                  [ 'lib'     ,[ ] ],
                  [ 'lib_src' ,[ ] ],
                  [ 'src'     ,['src/main.cpp'] ],
                  [ 'lib_type' ,'Shared' ],
               ],
            ],
        ]

    ##
    # @brief common config independent from configs (platforms,OS ...)
    #
    # @return common config value
def Get_output_common(): 
    return  [
                [ 'inc_path',['inc'] ],
                [ 'lib',['D_E_L_I_getPrjName_'] ],
                [ 'bin_file',[
                    [ 'res/*.*','res'],
                    ] 
                  ],

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
            [ 'bin_file',[
                ['out/x64_Linux_ubuntu/lib/libD_E_L_I_getPrjName_.so','lib'],
                ]
              ],
            [ 'lib_path',['out/x64_Linux_ubuntu/lib'] ],
        ]
      ],
      ['x64_Windows', 
        [
            [ 'inc_path',['inc/x64_Windows'] ],
            [ 'bin_file',[
                  ['out/x64_Windows/lib/D_E_L_I_getPrjName_.dll','lib'],
                ] 
              ],
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

def Do_pre_build(target_config):
    print("Do pre build job")

def Do_post_build(target_config):
    print("Do post build job")
    #remote_share_dir ="~/01_share/00_web_share"
    #outputdir = 'out/'+target_config+'/'
    #cmd="cp -r "+outputdir+"*"+" "+remote_share_dir
    #print("$ "+cmd)  
    #output=subprocess.call (cmd, shell=True)
    #print("Binary upload done")
