# -*- coding: utf-8 -*- 

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
        print('Already exist submodule['+sub_module_name+']['+sub_module_group+\
            '] file ['+filename+']')
        if ( filecmp.cmp(src_file_path,target_file_path) == False ) :
          print('The sub module file ['+src_file_path+\
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
    print('The module ['+module_name+']'+'['+module_group+']'+\
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
    print('The module ['+module_name+']'+'['+module_group+']'+\
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

      print('\n'+'module_ID:['+module_name+']['+module_group+'] \nmodule_output :'+str(module_output)+'\n')
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
        failures_message = "\n".join(["Failed building %s" % bf_to_str(x) 
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
    cmd ="cd "+top_path+'/'+group_name+'/'+module_name+' ;'+'scons CONFIG='\
        +target_config
    output=subprocess.call (cmd, shell=True)
    if (output !=0):
      ret = False
      print("\033[1;31mBuild Err on ["+module_name+"]-["+group_name+"]\033[m");
    else:
      print("\033[1;32mBuild Done ; ["+module_name+"]-["+group_name+"]\033[m");
  return ret

