#!/usr/bin/python3
import subprocess

import os
import os.path
import sys

## ver 0.2.0 (2017.01.03)   ; sub module include 시 환경변수 손상 문제 수정함
## ver 0.2.1 (2017.01.04)   ; sub module 복사시 환경변수 손상 문제 수정함, LINKFLAGS에 디폴트로 -pthread 추가
## ver 0.2.2 (2017.01.04)   ; test frame에서 라이브러리 링킹 순서 Append에서 Prepend로 수정함- 링킹에러 방지  
## ver 0.2.3 (2017.01.05)   ; 의존성 라이브러리 -c 옵션 들어올 시 지우도록 수정  

def setPrjName(name):
    global g_PrjName
    g_PrjName=name
def getPrjName():
    global g_PrjName
    return g_PrjName

def setGroupName(name):
    global g_GroupName
    g_GroupName=name
def getGroupName():
    global g_GroupName
    return g_GroupName


##
# @brief the name of the project
g_PrjName = ""

##
# @brief the name of the group
g_GroupName = ""
##
# @brief The path of the test framework ; ex) gtest, cpputest ...
g_TestFrame_Path = ""
def setTestFramework_Path(name):
    global g_TestFrame_Path
    g_TestFrame_Path = name
def getTestFramework_Path():
    global g_TestFrame_Path
    return g_TestFrame_Path

g_Delimeter_Items = [
      ['D_E_L_I_getPrjName_',getPrjName ],
      ['D_E_L_I_getGroupName_',getGroupName ],
      ['D_E_L_I_getTestFramework_Path_',getTestFramework_Path ],
    ]

def DoDelimeterReplace(text):
  output=text
  for item in g_Delimeter_Items:
    delimeter = item[0]
    replace_target = item[1]()
    output = output.replace(delimeter,replace_target)
  return output
# files ; run.sh
# files ; bd_settings.sh


def getScript_main_cpp() :
  return \
"""#include <stdio.h>
#include "libmodule.h"
int main(int argc, char *argv[])
{
    printf("Hello World\\n");
    printf("libmodule() = %d\\n",testmodule());
    return 0;
}
"""
def getScript_bd_common_py() :
  return \
"""# -*- coding: utf-8 -*- 

import os
import copy
import glob
import sys
import imp
import filecmp

from bd_settings import *
from bd_config import *

# Constants
DEF_LIB_PATH='lib_path'
DEF_INC_PATH='inc_path'
DEF_DEFAULT_SETTING_PATH='build_context'
DEF_DEFAULT_SETTING_MODULE='bd_settings'

def Get_Top_Path():
    return os.getcwd()+'/../../'

##
# @brief merge two items; make logical union(합집합) set
#
# @param items00[IN] ; item to merge
# @param items01[IN]
# @param attribute[IN]
#                   
#
# @return merged item list
def merge_items(items00,items01,attribute=None):
    output =[]
    itemsA = copy.deepcopy(items00)
    itemsB = copy.deepcopy(items01)
    for itemB in itemsB:
        chk_flag = False
        for itemA in itemsA:
            if (attribute ==None) :
                if itemB[0] == itemA[0]:
                    # If there is the same item, merge them
                    chk_flag = True
                    # merge the item
                    for item_inner01 in itemB[1]:
                        if (  (item_inner01 in itemA[1]) == False ):
                            itemA[1].append(item_inner01)
            else:
                if itemA[0] == attribute and itemB[0] == itemA[0]:
                    # If there is the same item, merge them
                    chk_flag = True
                    # merge the item
                    for item_inner01 in itemB[1]:
                        if (  (item_inner01 in itemA[1]) == False ):
                            itemA[1].append(item_inner01)
        if (attribute ==None) : 
            if chk_flag ==False:
                # If there is no same item, append it
                itemsA.append(itemB)
    return itemsA

##
# @brief Copy sub module's bin files to target module
#
# @param Top_Path               Top path of the modules
# @param target_module_ID     Target module that is using sub module
# @param sub_module_name        Sub module name
# @param src_config             Config to copy from sub module
# @param target_config          the target config to be copied
# @param file_list              File list to copy
#
# @return 
def Copy_Module_OutputFiles(Top_Path,target_module_ID,sub_module_ID,src_config,
        target_config,
        file_list):
  target_module_name = target_module_ID[0]
  target_module_group = target_module_ID[1]
  sub_module_name = sub_module_ID[0]
  sub_module_group = sub_module_ID[1]

  base_src_dir = Top_Path+'/'+sub_module_group+'/'+sub_module_name+'/'
  base_target_dir = Top_Path+'/'+target_module_group+'/'+target_module_name+'/'

  for filename in file_list:
    src_file_path= base_src_dir+'/'+filename
    target_file_path = base_target_dir+'/'+filename
    # check the existing of the file
    if os.path.isfile(src_file_path):
      # if the target file is not existed copy the source file
      if (os.path.isfile(target_file_path) ==False) :
        if os.path.isdir(os.path.dirname(target_file_path))==False :
          os.makedirs(os.path.dirname(target_file_path))
        shutil.copyfile(src_file_path,target_file_path)
      else:
        print('Already exist submodule['+sub_module_name+']['+sub_module_group+\\
            '] file ['+filename+']')
        if ( filecmp.cmp(src_file_path,target_file_path) == False ) :
          print('The sub module file ['+src_file_path+\\
              '] has been updated, now copy it')
          shutil.copyfile(src_file_path,target_file_path)

#
# @brief Set the absolute path of sub modules
#
# @param types[IN] the types list variable to apply the absolute path 
#                  ex) ['inc_path', 'lib_path']
# @param module_ID[IN] ex) ['SDL2_ttf','Support_Layer']
# @param module_output_ctx[IN] config data 
#                    ex) [
#                           ['x64_Linux_ubuntu',
#                              [
#                                [ 'inc_path',['inc/x64_Linux_ubuntu'] ],
#                                [ 'bin_file',['lib/libSDL2.so'] ],
#                                [ 'lib_path',['out/x64_Linux_ubuntu/lib'] ],
#                              ]
#                            ]
#                        ]
#
# @return module output context that are applied the absolute path
def Do_Convert_module_to_absolute_path(types,module_ID,
    module_output_ctx,top_path=Get_Top_Path()):
  module_name  = module_ID[0]
  module_group = module_ID[1]
  prefix = top_path+'/'+module_group+'/'+module_name  # absolute path's prefix
  for config_item in module_output_ctx:
    config_ctx =config_item[1]
    for env_var in config_ctx:
      if env_var[0] in types:
        cnt = 0
        for item in env_var[1]:
          env_var[1][cnt]= prefix+'/'+item
          cnt = cnt+1
  return module_output_ctx


##
# @brief Get environment var list from BD_Environment
#
# @param config[IN]     config of the environment value 
# @param env_type       environment value type(inc_path, lib_path ....)
#
# @return the list of the env. values
def Get_env_var(config,env_type):
    env_var_list=[]
    Bd_Environment = Get_Bd_Environment()
    for config_item in Bd_Environment:
        if config_item[0] == config :
            config_bd_env = config_item[1]
            for bd_env in config_bd_env:
                if (bd_env[0] == env_type):
                    env_var_list= bd_env[1]
    return env_var_list

def Get_Module_Dir_Path(module_name):
    return Get_Top_Path()+module_name

def Get_env_libsrc_files(selected_config):
    env_libsrc=Get_env_var(selected_config,'lib_src')
    file_list=[]
    for item in env_libsrc:
        file_list=file_list+glob.glob(item)
    return copy.deepcopy(file_list)

def Get_env_src_files(selected_config):
    env_libsrc=Get_env_var(selected_config,'src')
    file_list=[]
    for item in env_libsrc:
        file_list=file_list+glob.glob(item)
    return copy.deepcopy(file_list)

def Get_env_swut_files(selected_config):
    env_libsrc=Get_env_var(selected_config,'swut_src')
    file_list=[]
    for item in env_libsrc:
        file_list=file_list+glob.glob(item)
    return copy.deepcopy(file_list)

def Get_env_swit_files(selected_config):
    env_libsrc=Get_env_var(selected_config,'swit_src')
    file_list=[]
    for item in env_libsrc:
        file_list=file_list+glob.glob(item)
    return copy.deepcopy(file_list)



##
# @brief Get external module instance  
#        ;read the *.py file and get its instance
#        this function is for python 2.7x because scons is still using python 2.7
#
# @param file_path[IN] file path list of the target .py file
#                      ex) './build_context'
# @param file_name[IN] file name to import .py file BUT!, do not add '.py'
#                      ex) "bd_settings" , "bd_common".. NOT, "bd_settings.py"
#
# @return (True/False,instance) imported instance
def Get_ext_Module_inst(file_path,file_name):
  import imp
  try :
      fp,pathname,description = imp.find_module(file_name,[file_path])
  except ImportError :
      print('Err; err on reading module ['+file_name+']'+ 
          ' Cannot find the file ['+file_name+'] on paths ['+str(file_path)+']')
      return (False,None)

  # The following 1st argument (file_name+file_path) is for preventing
  # duplication of the module names
  # if the 1st arg is only file name, it causes the unexpected err
  #instance=imp.load_module(file_name+file_path,fp,pathname,description)
  instance=imp.load_module(file_name+Get_Module_ID()[0]+Get_Module_ID()[1],
      fp,pathname,description)
  
  fp.close()
  return (True,instance)

##
# @brief Get external module instance  
#        ;read the *.py file and get its instance
#        this function is for python 3.3x 
#
# @param file_path[IN] file path list of the target .py file
#                      ex) './build_context'
# @param file_name[IN] file name to import .py file BUT!, do not add '.py'
#                      ex) "bd_settings" , "bd_common".. NOT, "bd_settings.py"
#
# @return (True/False,instance) imported instance
def Get_ext_Module_inst_for_py3_3(module_file_path,module_name):
    import importlib
    full_path = module_file_path+'/'+module_name+'.py'
    spec=importlib.util.spec_from_file_location(module_name,full_path)
    try :
        instance=spec.loader.load_module()
    except FileNotFoundError :
        print('Err; err on reading module '+' Cannot find the module ['+module_name+'] on paths ['+str(module_file_path)+']')
        return (False,None)
    return (True,instance)
##
# @brief Get external module instance  
#        ;read the *.py file and get its instance
#        this function is for python 3.4x 
#
# @param file_path[IN] file path list of the target .py file
#                      ex) './build_context'
# @param file_name[IN] file name to import .py file BUT!, do not add '.py'
#                      ex) "bd_settings" , "bd_common".. NOT, "bd_settings.py"
#
# @return (True/False,instance) imported instance

def Get_ext_Module_inst_for_py3_4(module_file_path,module_name):
    import importlib
    full_path = module_file_path+'/'+module_name+'.py'
    loader = importlib.machinery.SourceFileLoader(module_name, full_path)
    try :
        instance=loader.load_module()
    except FileNotFoundError :
        print('Err; err on reading module '+' Cannot find the module ['+module_name+'] on paths ['+str(module_file_path)+']')
        return (False,None)
    return (True,instance)

##
# @brief Get all dependent module list recursively
#        the list contains its all sub's dependent contents
#        directories recursively
# @param module_ID[IN]    module ID to know its dependency
# @param top_path[IN]       top path of the modules
# @param setting_path[IN]   settings file path , ex) 'build_context'
# @param setting_module[IN]   setting module name ex) 'bd_settings'
#
# @return (True/False, list of the dependency modules)
def Get_all_dependent_list(module_ID,top_path=Get_Top_Path(),
      setting_path=DEF_DEFAULT_SETTING_PATH,
      setting_module=DEF_DEFAULT_SETTING_MODULE):
  module_list = []
  module_name = module_ID[0]
  module_group = module_ID[1]
  settings_file_path = top_path+'/'+module_group+'/'+module_name+'/'+setting_path


  # :x: get setting module instance
  ret = Get_ext_Module_inst(settings_file_path,setting_module)
  if ret[0] == True : 
    module_settings_instance = ret[1]
  else:
    return (False,None)

  try :
    sub_modules_info = module_settings_instance.Get_dependency_module_info()
    del module_settings_instance

  except AttributeError :
    print('The module ['+module_name+']'+' has no Get_dependency_module_info() Function')
    return (False,None)

  module_list=Get_dependency_module(sub_modules_info)

  if (module_list !=[]):
    for sub_module in module_list:
      ret =Get_all_dependent_list(sub_module,top_path,setting_path,setting_module)
      if (ret[0] == True):
        module_list= module_list + ret[1] 
      else:
        Get_ext_Module_inst(settings_file_path,setting_module)
        return (False,None)
  Get_ext_Module_inst(settings_file_path,setting_module)
  return (True,module_list)

def Get_Module_Output_env_var(module_ID,top_path=Get_Top_Path(),
        setting_path=DEF_DEFAULT_SETTING_PATH,
        setting_module=DEF_DEFAULT_SETTING_MODULE):
  output_env=[]
  module_name=module_ID[0]
  module_group=module_ID[1]
  settings_file_path = top_path+'/'+module_group+'/'+module_name+'/'+setting_path

  # Get common settings variables
  output_common = []
  # :x: get setting module instance
  ret = Get_ext_Module_inst(settings_file_path,setting_module)
  if ret[0] == True : 
    module_settings_instance = ret[1]
  else:
    return (False,None)
  try :
    output_common = module_settings_instance.Get_output_common()
    del module_settings_instance
  except AttributeError :
    print('The module ['+module_name+']'+'['+module_group+']'+\\
        ' has no Get_output_common() Function')
  # Get specific settings variables
  output_specific = []
  ret = Get_ext_Module_inst(settings_file_path,setting_module)
  if ret[0] == True : 
    module_settings_instance = ret[1]
  else:
    return (False,None)

  try :
    output_specific = module_settings_instance.Get_output_specific()
    del module_settings_instance
  except AttributeError :
    print('The module ['+module_name+']'+'['+module_group+']'+\\
        ' has no Get_output_specific() Function')
  output_env= output_env + Do_Convert_module_to_absolute_path(['lib_path','inc_path'],module_ID,Get_output_configs(output_specific,output_common ) )
  return (True,output_env)

  ##
  # @brief Get dependency module list
  #
  # @param module_info[IN] module dependency info 
  #                        ex) [
  #                              [
  #                                 ['SDL2','Support_Layer'],
  #                                  {
  #                                    'x64_Linux_ubuntu':'x64_Linux_ubuntu',
  #                                    'x64_Windows':'x64_Windows',
  #                                    'arm_Android':'arm_Android'
  #                                  }
  #                              ],
  #                            ]
  #
  # @return dependency module list
def Get_dependency_module(sub_module_info): 
    dependency_module_list =[]
    if (sub_module_info == [[]]):
        return dependency_module_list
    for dependency_module in sub_module_info:
        dependency_module_list.append(dependency_module[0])
    return dependency_module_list 



##
# @brief copy dependent binaries recursively 
# @param Target_module_ID[IN] Target module ID to know its dependency
#
# @return 

def Copy_Dependent_Files_on_Sub_module(Target_module_ID=Get_Module_ID(),
    target_config=None):

  ret = Get_all_dependent_list(Target_module_ID)
  if (ret[0] == True):
      module_IDs = ret[1]
  else :
      return (False,None)
  print('module names ='+str(module_IDs))
  for module_ID in module_IDs:
      connected_config = Get_config_from_dependency_info(module_ID,target_config)
      # Get module's output context
      ret = Get_Module_Output_env_var(module_ID)
      if (ret[0]==True):
        module_output=ret[1]
      else:
        return (False,None)
      # Get Modules's bin_file attribute for each configs
      for output_config in module_output:
        print('target_config :'+str(target_config)+' output_config : '+str(output_config[0]))
        print('connected_config :'+str(connected_config))
        if (target_config != None and connected_config != output_config[0]):
          continue
        for item in output_config[1]:
          if item[0]=='bin_file':
            Copy_Module_OutputFiles(Get_Top_Path(),Target_module_ID,
                module_ID,output_config[0],target_config,item[1])


def make_dirs(target_config, dirs,out_dir='./out'):
    for item in dirs:
        dirpath=out_dir+'/'+target_config+'/'+item
        if os.path.isdir(dirpath)==False :
            os.makedirs(dirpath)

##
# @brief find the associated config name from dependency info
#
# @param connected_module_ID  ex)['SDL2','Support_Layer'],['Widget','App_Layer']
#                                 ...the module ID
# @param config     config to find ex)  'x64_Linux_ubuntu'
# @param dependency_module_info ex)[
#                                     [
#                                       ['SDL2','Support_Layer'],
#                                       {
#                                         'x64_Linux_ubuntu':'x64_Linux_ubuntu',
#                                         'x64_Linux_ubuntu_integ_test':'x64_Linux_ubuntu',
#                                         'x64_Windows':'x64_Windows',
#                                         'arm_Android':'arm_Android',
#                                       }
#                                     ],
#                                     [
#                                       ['SDL2_ttf','Support_Layer'],
#                                       {
#                                         'x64_Linux_ubuntu':'x64_Linux_ubuntu',
#                                         'x64_Linux_ubuntu_integ_test':'x64_Linux_ubuntu',
#                                         'x64_Windows':'x64_Windows',
#                                         'arm_Android':'arm_Android',
#                                       }
#                                     ]
#
#                                  ]
#
# @return the submodule config which is mapped by config
def Get_config_from_dependency_info(connected_module_ID,config,dependency_module_info=Get_dependency_module_info()):   
    ret = config
    connected_module_name = connected_module_ID[0]
    connected_module_group = connected_module_ID[1]
    #find module item and its connected config
    for module in dependency_module_info:
        module_name = module[0][0]
        module_group = module[0][1]
        module_config_mapping = module[1]
        if (connected_module_name == module_name
            and connected_module_group == module_group):
            #if module info is not exist it should return same config
            if (module_config_mapping == None):
                ret = config
            else :
                ret = module_config_mapping[config]
    return ret
    

def Do_Setup_Bd_Env(target_config,Target_module_ID=Get_Module_ID()):
  print("+++ Build Env +++ ; "+target_config)
  # Set the build env variables
  Bd_Environment = Get_Bd_Environment()

  # make output directories
  make_dirs(target_config,Get_output_dirs())
  # Copy depedency files on sub modules
  # Find all dependent files recusrively and copy them


  Copy_Dependent_Files_on_Sub_module(Target_module_ID,target_config)
  
  
  for config_env in Bd_Environment:
      config_env[1] = copy.deepcopy( merge_items( config_env[1], Get_common_bd_env()) )
  Set_Bd_Environment(Bd_Environment)

  # Get the env variables on sub modules & applying on build env varibale
  module_IDs = Get_dependency_module(Get_dependency_module_info())
  
  for module_ID in module_IDs:
      module_name=module_ID[0]
      module_group=module_ID[1]
      # Get module's output context
      module_output=[]
      settings_file_path = Get_Top_Path()+'/'+module_group+'/'+module_name+'/'+DEF_DEFAULT_SETTING_PATH 

      # CAUTION_00!!! : 아래 루틴 처럼 서브 모듈의 bd_settings.py를 읽으면 
      # Get_Bd_Environment()와 연결된 전역변수 g_Bd_Environment가 초기화 되는 현상 발견
      # 회피하기 위해서 Get_ext_Module_inst호출 전에 g_Bd_Environment를 Bd_Environment
      # 를 저장한다, 이는 설계 로직 문제보다 파이선 버그에 가깝다
      ret = Get_ext_Module_inst(settings_file_path,DEF_DEFAULT_SETTING_MODULE)

      if ret[0] == True : 
          module_settings_instance = ret[1]
      else:
          return (False,None)

      try :
          module_output= Get_output_configs(module_settings_instance.Get_output_specific(),module_settings_instance.Get_output_common())
          del module_settings_instance
      except AttributeError :
          print('The module ['+module_name+']['+module_group+'] has no Get_output_configs() or Get_output_specific() Function')
          continue
      # Get Modules's lib_path, inc_path,lib attributes for each configs
      # convert inc_path, lib_path attribute to absolute path
      ret =Get_Module_Output_env_var(module_ID)
      if (ret[0]==True):
          module_output=ret[1]
      else:
          return (False,None)

      print('\\n'+'module_ID:['+module_name+']['+module_group+'] \\nmodule_output :'+str(module_output)+'\\n')
      for output_config in module_output:
          # CAUTION ; 상기 언급된 초기화 문제(CAUTION_00)로 아래 루틴 제거
          #Bd_Environment = Get_Bd_Environment()
          for config_env in Bd_Environment :
              if (Get_config_from_dependency_info(module_name,config_env[0]) == output_config[0]) :
                  config_env[1]=merge_items(config_env[1],output_config[1],'lib')
                  config_env[1]=merge_items(config_env[1],output_config[1],'inc_path')
                  config_env[1]=merge_items(config_env[1],output_config[1],'lib_path')
          # CAUTION ; 상기 언급된 초기화 문제(CAUTION_00)로 아래 루틴 제거
          #Set_Bd_Environment(Bd_Environment )

  Set_Bd_Environment(Bd_Environment )

  

def Get_output_configs(output_specific, output_common): 
  for specific_item in output_specific:
      # common configs should be applied on each specific config
      specific_item[1]= merge_items(specific_item[1],output_common)
  return output_specific


##
# @brief Selection of Target CONFIG
#
# @param arglist[IN]            arguments from SCons
# @param default_config[IN]     default build config
# @param config_dic[IN]         configurations dic
#
# @return (True/False,config)   target configuration
def Get_target_config(arglist,default_config,config_dic):
    #type checking
    if type(arglist) is not list:
        return (False,None)
    if type(default_config) is not str:
        return (False,None)
    if default_config =='':
        return (False,None)

    TARGET_CONFIG=''
    # Selection of Target CONFIG
    for key, value in arglist:
        if key == 'CONFIG':
            for CONFIG in config_dic:
                if value == CONFIG:
                    TARGET_CONFIG=CONFIG
    if TARGET_CONFIG=='':
        TARGET_CONFIG=default_config
        print('Default target CONFIG selected : '+TARGET_CONFIG)

    return True,TARGET_CONFIG

def bf_to_str(bf):                                         
    #Convert an element of GetBuildFailures() to a string
    #in a useful way.
    import SCons.Errors                                    
    if bf is None: # unknown targets product None in list  
        return '(unknown tgt)'                             
    elif isinstance(bf, SCons.Errors.StopError):           
        return str(bf)                                     
    elif bf.node:                                          
        return str(bf.node) + ': ' + bf.errstr             
    elif bf.filename:                                      
        return bf.filename + ': ' + bf.errstr              
    return 'unknown failure: ' + bf.errstr                 

def build_status():                                                       
    #Convert the build status to a 2-tuple, (status, msg).
    from SCons.Script import GetBuildFailures                             
    bf = GetBuildFailures()                                               
    if bf:                                                                
        # bf is normally a list of build failures; if an element is None, 
        # it's because of a target that scons doesn't know anything about.
        status = 'failed'                                                 
        failures_message = "\\n".join(["Failed building %s" % bf_to_str(x) 
                                for x in bf if x is not None])            
    else:                                                                 
        # if bf is None, the build completed successfully.                
        status = 'ok'                                                     
        failures_message=''                                               
    return (status,failures_message)                                      


def display_build_status(target_config):
    #Display the build status. Called by atexit.              
    #Here you could do all kinds of complicated things       
    status, failures_message = build_status()                   
    if status == 'failed':                                      
        print "FAILED!!!!" # could display alert, ring bell, etc.
    elif status == 'ok':                                        
        print "Build succeeded."                                
        try :
            Do_post_build(target_config)                                         
        except NameError :
            print "No Post build function"                                

    print failures_message                                      

def Do_dependent_module_build(target_config,
  dependency_module_info=Get_dependency_module_info(),top_path=Get_Top_Path()):
  ret = True
  for module_item in dependency_module_info:
    module_name = module_item[0][0]
    group_name  = module_item[0][1]
    print("Build dependent module ;["+module_name+"]-["+group_name+"]" )
    cmd ="cd "+top_path+'/'+group_name+'/'+module_name+' ;'+'scons CONFIG='\\
        +target_config
    output=subprocess.call (cmd, shell=True)
    if (output !=0):
      ret = False
      print("\\033[1;31mBuild Err on ["+module_name+"]-["+group_name+"]\\033[m");
    else:
      print("\\033[1;32mBuild Done ; ["+module_name+"]-["+group_name+"]\\033[m");
  return ret

"""
def getScript_bd_settings_py() :
  return \
"""# -*- coding: utf-8 -*- 
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
g_Bd_Environment = [
            ['x64_Linux_ubuntu',
               [
                  ['inc_path',[ ] ],
                  ['lib_path',[ ] ],
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
                [ 'lib',['D_E_L_I_getPrjName_'] ],
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
                    [ 'bin_file',['out/x64_Linux_ubuntu/lib/libD_E_L_I_getPrjName_.so'] ],
                    [ 'lib_path',['out/x64_Linux_ubuntu/lib'] ],
                ]
            ],
            ['x64_Windows', 
                [
                    [ 'inc_path',['inc/x64_Windows'] ],
                    [ 'bin_file',['out/x64_Windows/lib/D_E_L_I_getPrjName_.dll'] ],
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
"""
def getScript_SConstruct() :
  return \
"""# -*- coding: utf-8 -*- 
import os
import sys
import glob
import atexit
import multiprocessing

sys.path.append("./build_context")
from bd_config import *
from bd_common import *

# make builder ==============================
common_env = Environment()

# get Target config  ========================
TARGET_CONFIG=''
ret= Get_target_config(ARGLIST,DEFAULT_CONFIG,CONFIG_DIC)
if (ret[0] == False):
    print('Error on setting Target config')
    exit(1)
else:
    TARGET_CONFIG = ret[1]
if TARGET_CONFIG == '':
    print('Error on setting Target config')
    exit(1)
# ===========================================

# dependent module builds ===================
if (GetOption('clean') != True) :
    if (Do_dependent_module_build(TARGET_CONFIG) != True ):
        exit(1)
# ===========================================

# Setup Build Environment ===========
Do_Setup_Bd_Env(TARGET_CONFIG)
# ===================================
# remove dependency libraries
if (GetOption('clean') == True) :
    for item in glob.glob('out/'+TARGET_CONFIG+'/lib/*'):
        os.remove(item)

# default build execution option
# Set Number of CPU ===============================
num_cpu = int(os.environ.get('NUM_CPU',multiprocessing.cpu_count()))
SetOption('num_jobs', num_cpu)
print('Number of CPU in the system : '+str(num_cpu))
# =================================================

# Post Build procedure ============================
if (GetOption('clean') != True) :
  atexit.register(display_build_status,TARGET_CONFIG)
# =================================================

LIBS            = Get_env_var(TARGET_CONFIG,'lib')
LIBPATH         = Get_env_var(TARGET_CONFIG,'lib_path')
INCDIR          = Get_env_var(TARGET_CONFIG,'inc_path')
CFLAGS          = Get_env_var(TARGET_CONFIG,'cflags')
CPPFLAGS        = Get_env_var(TARGET_CONFIG,'cppflags')
CCFLAGS         = Get_env_var(TARGET_CONFIG,'ccflags')

LIBSRC_FILES    = Get_env_libsrc_files(TARGET_CONFIG)
SRC_FILES       = Get_env_src_files(TARGET_CONFIG)
SWUT_FILES      = Get_env_swut_files(TARGET_CONFIG)
SWIT_FILES      = Get_env_swit_files(TARGET_CONFIG)

LIB_TYPE        = Get_env_var(TARGET_CONFIG,'lib_type')

TEST_INCDIR     = Get_env_var(TARGET_CONFIG,'test_inc_path')
TEST_LIBS       = Get_env_var(TARGET_CONFIG,'test_lib')
TEST_LIBPATH    = Get_env_var(TARGET_CONFIG,'test_lib_path')

# The name of the output file ===================================
TARGET_NAME=Get_Module_Name()
SHLIBPREFIX = CONFIG_DIC[TARGET_CONFIG]['SHLIBPREFIX']
SHLIBSUFFIX = CONFIG_DIC[TARGET_CONFIG]['SHLIBSUFFIX']
PROGSUFFIX  = CONFIG_DIC[TARGET_CONFIG]['PROGSUFFIX']

if (Get_env_var(TARGET_CONFIG,'target_lib_name') ==[]):
    if (LIB_TYPE == 'Shared') :
        TARGET_LIB_FILE='lib/'+SHLIBPREFIX+TARGET_NAME+SHLIBSUFFIX
    elif(LIB_TYPE == 'Static') :
        TARGET_LIB_FILE='lib/'+'lib'+TARGET_NAME+'.a'
else :
    if (LIB_TYPE == 'Shared') :
        TARGET_LIB_FILE='lib/'+SHLIBPREFIX+Get_env_var(TARGET_CONFIG,'target_lib_name')+SHLIBSUFFIX
    elif(LIB_TYPE == 'Static') :
        TARGET_LIB_FILE='lib/'+'lib'+Get_env_var(TARGET_CONFIG,'target_lib_name')+'.a'
    TARGET_NAME=Get_env_var(TARGET_CONFIG,'target_lib_name')

if (Get_env_var(TARGET_CONFIG,'target_bin_name') ==[]):
    TARGET_EXE_FILE='bin/'+TARGET_NAME+PROGSUFFIX
else :
    TARGET_EXE_FILE='bin/'+Get_env_var(TARGET_CONFIG,'target_bin_name')
#================================================================

Target_env = common_env.Clone()
# Apply the environment values on Target environment
for key in CONFIG_DIC[TARGET_CONFIG]:
    Target_env[key] = CONFIG_DIC[TARGET_CONFIG][key]

Target_env.Append(CPPPATH=INCDIR)
Target_env.Append(CPATH=INCDIR)
Target_env.Append(CFLAGS=CFLAGS)
Target_env.Append(CPPFLAGS=CPPFLAGS)
Target_env.Append(CCFLAGS=CCFLAGS)
Target_env.Append(LIBS=LIBS)
Target_env.Append(LIBPATH=LIBPATH)

Test_env = Target_env.Clone()
Test_env.Append(CPPPATH=TEST_INCDIR)
Test_env.Append(CPATH=TEST_INCDIR)
Test_env.Prepend(LIBS=TEST_LIBS)
Test_env.Prepend(LIBS=[TARGET_NAME])
Test_env.Append(LIBPATH=TEST_LIBPATH)

Export('LIB_TYPE')
Export('Target_env')
Export('Test_env')
Export('TARGET_LIB_FILE')
Export('TARGET_EXE_FILE')
Export('LIBSRC_FILES')
Export('SRC_FILES')
Export('TARGET_NAME')
Export('LIBS')
Export('SWUT_FILES')
Export('SWIT_FILES')

SConscript('./SConscript',variant_dir='out/'+TARGET_CONFIG,duplicate=0)
"""
def getScript_libmodule_h() :
  return \
"""#ifndef _LIBMODULE_H_
#define _LIBMODULE_H_

int testmodule();
#endif // :X: #ifndef _LIBMODULE_H_
"""
def getScript_bd_sh() :
  return \
"""#!/bin/bash
scons -Q --debug=time CONFIG=x64_Linux_ubuntu $*
#scons -Q --debug=time CONFIG=x64_Windows $*
"""
def getScript_libmodule_cpp() :
  return \
"""
int testmodule()
{
    return 7;
}
"""
def getScript_bd_config_py() :
  return \
"""# -*- coding: utf-8 -*- 
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
"""
def getScript_run_sh() :
  return \
"""#!/bin/bash
export LD_LIBRARY_PATH=out/x64_Linux_ubuntu/lib
out/x64_Linux_ubuntu/bin/D_E_L_I_getPrjName_ $*
"""
def getScript_SConscript() :
  return \
"""# -*- coding: utf-8 -*- 
Import('LIB_TYPE')
Import('Target_env')
Import('Test_env')
Import('TARGET_LIB_FILE')
Import('TARGET_EXE_FILE')
Import('LIBSRC_FILES')
Import('SRC_FILES')
Import('TARGET_NAME')
Import('LIBS')
Import('SWUT_FILES')
Import('SWIT_FILES')

if (LIB_TYPE == 'Shared') :
    LIB_BUILDER=Target_env.SharedLibrary(TARGET_LIB_FILE,source=LIBSRC_FILES)
elif(LIB_TYPE == 'Static') :
    LIB_BUILDER=Target_env.StaticLibrary(TARGET_LIB_FILE,source=LIBSRC_FILES)

EXE_BUILDER=Target_env.Program(TARGET_EXE_FILE,SRC_FILES,LIBS=[TARGET_NAME]+LIBS)

if (SWUT_FILES != [] and SWIT_FILES != [] ):
    SWUT_BUILDER=Test_env.Program(TARGET_EXE_FILE+'_swut',SWUT_FILES)
    SWIT_BUILDER=Test_env.Program(TARGET_EXE_FILE+'_swit',SWIT_FILES)
    Depends( SWUT_BUILDER,TARGET_LIB_FILE)
    Depends( SWIT_BUILDER,TARGET_LIB_FILE)

Depends( EXE_BUILDER,TARGET_LIB_FILE)
"""
def getScript_swut_main_cpp() :
  return \
"""#include <gtest/gtest.h>
#include "libmodule.h"

// Test template    

class SampleTest : public testing::Test {
    protected:
        virtual void SetUp() {
        }
        virtual void TearDown() {
        }
};
 
TEST_F(SampleTest, BasicTest00) {
    EXPECT_EQ(2, (1+1));
    EXPECT_EQ(5, (2+3));
    EXPECT_EQ(testmodule(), 7);
}


int main(int argc, char *argv[])
{
    char bus_addr[1024] ={ 0 , };
    char cmd[2048] ={ 0 , };
    int custom_argc=2;
    char* pArgv[2];
    char* pCmd1 =(char*)"--gtest_output=xml:swut_report.xml";
    pArgv[1] = pCmd1;

    ::testing::InitGoogleTest(&custom_argc,(char**)pArgv);
    return RUN_ALL_TESTS();
}
"""
def getScript_swit_main_cpp() :
  return \
"""#include <gtest/gtest.h>
#include "libmodule.h"
// Test template    

class SampleTest : public testing::Test {
    protected:
        virtual void SetUp() {
        }
        virtual void TearDown() {
        }
};
 
TEST_F(SampleTest, BasicTest00) {
    EXPECT_EQ(2, (1+1));
    EXPECT_EQ(5, (2+3));
    EXPECT_EQ(testmodule(), 7);
}


int main(int argc, char *argv[])
{
    char bus_addr[1024] ={ 0 , };
    char cmd[2048] ={ 0 , };
    int custom_argc=2;
    char* pArgv[2];
    char* pCmd1 =(char*)"--gtest_output=xml:swit_report.xml";
    pArgv[1] = pCmd1;

    ::testing::InitGoogleTest(&custom_argc,(char**)pArgv);
    return RUN_ALL_TESTS();
}
"""



# directory names ========================
def get_dirRoot():
    return ""
def get_dir_lib():
    return "lib"
def get_dir_inc():
    return "inc"
def get_dir_libsrc():
    return "libsrc"
def get_dir_out():
    return "out"
def get_dir_res():
    return "res"
def get_dir_src():
    return "src"
def get_dir_build_ctx():
    return "build_context"
def get_dir_testframe():
    return "testframework"
def get_dir_integ_test():
    return get_dir_testframe()+"/"+"swit"
def get_dir_unit_test():
    return get_dir_testframe()+"/"+"swut"
#  ========================================



# Prj Contents item's offsets #####
g_Contents_Offset_Contents_Name = 0
g_Contents_Offset_Directory = 1
g_Contents_Offset_Contents_File = 2
# #################################

# Prj Contents item 
g_Prj_Contents = [
        # contents name,        directory,  contents_files[filename, fileText],
        ["Project root",        get_dirRoot,[
                                                ["SConstruct",getScript_SConstruct],
                                                ["SConscript",getScript_SConscript],
                                                ["bd.sh",getScript_bd_sh],
                                                ["run.sh",getScript_run_sh],
                                            ]
                                                    ],
        ["include directory",   get_dir_inc,[
                                                ["libmodule.h",getScript_libmodule_h],
                                            ] 
                                                    ],
        ["lib directory",       get_dir_lib, [] ],
        ["libsrc directory",    get_dir_libsrc, [
                                                    ["libmodule.cpp",getScript_libmodule_cpp],
                                                ] 
                                                    ],
        ["out directory",       get_dir_out, [] ],
        ["resource directory",  get_dir_res, [] ],
        ["source directory",    get_dir_src,    [
                                                    ["main.cpp",getScript_main_cpp],
                                                ] 
                                                ],
        ["build context directory", get_dir_build_ctx, [
                                                    ["bd_common.py",getScript_bd_common_py],
                                                    ["bd_config.py",getScript_bd_config_py],
                                                    ["bd_settings.py",getScript_bd_settings_py],
                                                   ] 
                                                   
                                                    ],
        ["testframe directory", get_dir_testframe, [] ],
        ["integ test directory",get_dir_integ_test, [
                                                        ["swit_main.cpp",getScript_swit_main_cpp],
                                                    ] 
                                                        ],
        ["unit test directory", get_dir_unit_test, [
                                                        ["swut_main.cpp",getScript_swut_main_cpp],
                                                    ] 
                                                        ],
        
        ]


##
# @brief check the directory if not exist make it
#
# @param targetPath[IN] the path to make
#
# @return True when it success
def check_directory_or_make(targetPath):
    print ('make [',targetPath, '] directory')
    if os.path.isdir(targetPath) == False:
        if os.makedirs(targetPath) == False:
            return False
    else:
        print (targetPath,"is already exist")
    return True

##
# @brief 
#
# @param contents [ filename, script to write, write mode 'w'(write) 'a'(add) ]
#        ex) [makefile,g_script_makefile,'w']
# @return 
def add_script(contents):
    writeFlag=False
    targetfilename = contents[0]
    scriptcontents = contents[1]
    writemode = contents[2]
    
    if writemode == 'a' and os.path.isfile(targetfilename) == True :
        # :x: to prevent rewriting same script
        f = open(targetfilename,'r')
        script = f.read()
        if script.find('# _:x:_ Add Script for the dev. environment') == -1 :
            writeFlag = True
        else :
            print("the script for "+targetfilename+" is already existed")
        f.close()
    elif writemode =='w' :
        writeFlag = True

    if writeFlag == True :
        f = open(targetfilename,writemode)
        scriptcontents=DoDelimeterReplace(scriptcontents)
        f.write(scriptcontents)
        f.close()
    if writemode == 'w' :
        os.chmod(targetfilename,0o700)
    return True


def makePrjContents(prjName,groupName,Prj_Contents):
    print("Generate Directories")
    
    # :x: make project root directory
    #if check_directory_or_make(prjName) == False :
    #    print('Error on ',item)
    #    return False

    for item in Prj_Contents :
        # make directories
        dir_item =groupName+'/'+prjName+"/"+item[g_Contents_Offset_Directory]()+"/"
        if check_directory_or_make(dir_item) == False :
            print('Error on ',item)
            return False

        # make contents files
        for fileitem in item[g_Contents_Offset_Contents_File] :
            contents=[dir_item+fileitem[0],fileitem[1](),'w']
            print("\tAdd script [ "+contents[0])
            if add_script(contents) == False:
                    print('Error on ',fileitem[0])
                    return False

        


def printusage():
    print( "***Usage***")
    print( "$ "+ sys.argv[0]+" project_name group_name homepath_of_the_gtest\n")
    print( "ex) \n")
    print( "$ "+ sys.argv[0]+" myprj Application_layer /home/myaccount/gtest-3.7.1\n\n")

def main(args):
    print ("MOBS ; Module Oriented Build System")
    print (" by windheim\n\n")
    print ("ver 0.0.2 2016.12.23 scons based scripts are placed\n\n")
    print ("ver 0.0.1 2016.09.10 initial verison\n\n")
    if len(args) == 2 :
        setPrjName (args[0])
        setGroupName (args[1])
        setTestFramework_Path(os.getenv("HOME")+"/gtest/googletest")
    elif len(args) == 0 :
        setPrjName ("Test")
        setGroupName ("Test_Layer")
        setTestFramework_Path(os.getenv("HOME")+"/gtest/googletest")
    elif len(args) == 3 :
        setPrjName( args[0])
        setGroupName (args[1])
        setTestFramework_Path(args[2])
    else :
        printusage()
        return False
        
    print ("Project module name ; "+getPrjName() + "\n\n")
    print ("Project group name ; "+getGroupName() + "\n\n")
    print ("Home Path of gtest ; "+getTestFramework_Path() + "\n\n")
    global g_PrjName
    global g_Prj_Contents
    makePrjContents(getPrjName(),getGroupName(),g_Prj_Contents)
   
if __name__ == '__main__':
    main(sys.argv[1:])
