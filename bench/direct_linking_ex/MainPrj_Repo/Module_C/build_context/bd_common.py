#!/usr/bin/python2
# -*- coding: utf-8 -*- 
import abc
import copy
import os
import glob
import subprocess

import pdb
import shutil

##
# @brief Default Context files' directory path
DEF_DEFAULT_CTX_PATH='./build_context/'
##
# @brief Default Settings file base name
DEF_DEFAULT_SETTINGS_MODULE='bd_settings.py'
##
# @brief Default Config file base name
DEF_DEFAULT_CONFIG_MODULE='bd_config.py'

##
# @brief Default build output directory path
DEF_DEFAULT_OUT_PATH='./out/'

class CtxInitErr(Exception):
  def __str__(self):
    return 'build context Initiation Err'

##
# @brief Get external module instance  
#        ; read the *.py file and get its instance
#        this function is for python 2.7x 
#        because scons is still using python 2.7
#
# @param file_path[IN] file path list of the target .py file
#                      ex) './build_context'
# @param base_file[IN] file name to import .py 
#
# @return (True/False,instance) imported instance
def Get_ext_Module_inst(file_path,base_file,ModuleID=None):

  if (file_path == None or base_file == None):
    return (False,None)
  module_name = os.path.splitext(base_file)[0]
  import imp
  try :
      fp,pathname,description = imp.find_module(module_name,[file_path])
  except ImportError :
      print('\033[1;31mErr; err on reading module ['+module_name+']'+ 
        ' Cannot find the file ['+base_file+'] on paths ['+str(file_path)+']'
        +'\033[m')
      print("\033[1;31mErr; cur dir ["+str(os.getcwd())+"]\033[m")

      return (False,None)

  if (ModuleID == None):
    instance=imp.load_module(module_name,
        fp,pathname,description)
  else :
    # The following 1st argument (module_name+file_path) is for preventing
    # duplication of the module names
    # if the 1st arg is only file name, it causes the unexpected err
    instance=imp.load_module(module_name+ModuleID.m_ModuleName
        +ModuleID.m_GroupName,
        fp,pathname,description)
  fp.close()
  return (True,instance)

class ModuleID :
  def __init__(self,module_ID):
    if type(module_ID) is not list:
      raise CtxInitErr
    self.m_ModuleID = copy.deepcopy(module_ID)
    self.m_ModuleName = self.m_ModuleID[0]
    self.m_GroupName  = self.m_ModuleID[1]

  ##
  # @brief This is for getting hashable name of Module ID
  #
  # @return total name of the ModuleID with delimeter '_+_'
  def GetTotalName(self):
    total_name=''
    for item in self.m_ModuleID:
      total_name=total_name+item+'_+_'
    return total_name

  def size(self):
    return len(self.m_ModuleID)
  def GetTopPath(self):
    path = ''
    for item in self.m_ModuleID:
      path += '../'
    return path
  def GetModulePath(self):
    path = ''
    for item in self.m_ModuleID:
      path = item+'/'+ path
    return path
  def __del__(self):
    return

class ModuleCtx :
  m_ModuleCtx_Dic = {}
  def __init__(self, ModuleID_input = None, 
    ctx_path_input = DEF_DEFAULT_CTX_PATH,
    settings_file = DEF_DEFAULT_SETTINGS_MODULE,
    config_file = DEF_DEFAULT_CONFIG_MODULE
    ):

    # initialization of the member variables ==============

    ##
    # @brief Module ID ; class ModuleID
    self.m_ModuleID=None
    ##
    # @brief context files' path ; default './build_context/'
    self.m_ctx_path=None

    ##
    # @brief target config to build
    self.m_Target_Config = None
    ##
    # @brief module settings file base name(=without extention-'.py')
    #        default ; 'build_settings'
    self.m_setting_base_file=None
    ##
    # @brief module config file base name(=without extention-'.py')
    #        default ; 'build_config'
    self.m_config_base_file=None 
    ##
    # @brief Default Config ex) 'x64_Linux_ubuntu'...'x64_Windows'..
    self.m_Default_Config=None
    # Module Settings Context Info
    self.m_Dependency_Module_Info=None
    self.m_Dependency_Module = []
    ##
    # @brief build environment ; common between configs
    self.m_Build_Env_Common=None
    ##
    # @brief build environment ; specific in config
    self.m_Build_Env_Specific=None
    ##
    # @brief build environment ; merged specific & common values
    self.m_Build_Env=None
    ##
    # @brief output items ; .so library, binary, resources(.png, .ttf)
    self.m_Output_Common=None
    self.m_Output_Specific=None
    self.m_Output = None
    ##
    # @brief output directory list ; ex) ['res', 'lib', 'bin', 'doc',...]
    self.m_Output_Dir=None

    self.m_PreBuildJob=None
    self.m_PostBuildJob=None

    # Module Config Context Info
    self.m_Config_Dictionary=None
    
    # Module Target Name ; same as lib name except prefix 
    #                      like -lModule_A  --> Module_A
    self.m_Target_Name={}
    # Target Library file name
    self.m_Target_LIB_file = {}
    # Target Binary file name
    self.m_Target_EXE_file = {}
    # SW integration test runner file name
    self.m_SWIT_RUNNER_file = {}
    # SW unit test runner file name
    self.m_SWUT_RUNNER_file = {}

    # Collect flag ; if this value is true, copying dependency binary files to
    #                local output directory
    self.m_Collect_flag = False 
    # End ====initialization of the member variables ==============

    if (os.path.splitext(settings_file)[1] != '.py'):
      print("\033[1;31mErr;setting file path "+
        str(settings_file)+"\033[m\n")
      raise CtxInitErr

    if (os.path.splitext(config_file)[1] != '.py'):
      print("\033[1;31mErr; config file path "+str(config_file)+"\033[m\n")
      raise CtxInitErr
    ctx_path = ''
    # Get Module ID if ModuleID_input is None
    if (ModuleID_input == None):
      ctx_path = ctx_path_input
      # read bd_settings.py file and get Module ID
      ret = Get_ext_Module_inst(ctx_path,settings_file)
      if (ret[0] == False):
        print("\033[1;31mErr ; Class [ModuleCtx] settings Initiation Error("
            +ctx_path
            +")("+settings_file+") \033[m");
        raise CtxInitErr
      module_inst = ret[1]
      try :
        moduleID = ModuleID(module_inst.Get_Module_ID())
      except AttributeError :
        print("\033[1;31m  AttributeError on "+settings_file+" \033[m\n");
        raise CtxInitErr
    elif (isinstance(ModuleID_input, ModuleID)):
      moduleID = ModuleID_input
      ctx_path = moduleID.GetTopPath()+moduleID.GetModulePath()+ctx_path_input
    else :
      print("\033[1;31mErr; Get Module ID Error ; Chk Module ID Value\033[m\n");
      raise CtxInitErr

    # read bd_config.py file and get Default Config 
    ret = Get_ext_Module_inst(ctx_path,config_file,
        moduleID)
    if (ret[0] == False):
      print("\033[1;31m Class [ModuleCtx] config Initiation Error("
          +ctx_path
          +")("+config_file+")(curdir;["+os.getcwd()+"] \033[m\n");
      raise CtxInitErr
    module_inst = ret[1]
    try :
      default_config = module_inst.DEFAULT_CONFIG
    except AttributeError :
      print("\033[1;31m Err ; AttributeError on "+settings_file+" \033[m\n");
      raise CtxInitErr
    
    self.m_ModuleID = copy.deepcopy(moduleID)
    self.m_ctx_path = copy.deepcopy(ctx_path)
    self.m_Default_Config = copy.deepcopy(default_config)
    self.m_setting_base_file = copy.deepcopy(settings_file)
    self.m_config_base_file = copy.deepcopy(config_file)

    if (self.ReadModuleCtx() == False):
      print("\033[1;31m Read Module Err  \033[m\n");
      raise CtxInitErr
 
    return
  ##
  # @brief merge two items; make logical union(합집합) set
  #
  # @param items00[IN] ; item to merge
  # @param items01[IN]
  # @param attribute[IN]
  #                   
  #
  # @return merged item list
  def merge_items(self,items00,items01,attribute=None):
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
  # @brief get absolute file/path names from relative ones 
  #
  # @param relative_path[IN] the wildcard list to find
  #               ex) ['inc',
  #                 '../../MainPrj_Repo/Module_B/inc/x64_Linux_ubuntu']
  #
  # @return the list trimed to absolute path
  def Get_ABS_path(self,relative_path):
    file_path_list = []
    for item in relative_path:
        file_path_list.append(os.path.abspath(item))
    return copy.deepcopy(file_path_list)


  ##
  # @brief get file names from wildcard list
  #
  # @param src_file_wildcard[IN] the wildcard list to find
  #                            ex) ['libsrc/*.cpp','libsrc/sub00/*.cpp']
  #
  # @return 
  def Get_files_from_wildcard(self,src_file_wildcard):
    file_list = []
    for item in src_file_wildcard:
      if (os.path.isfile(item) == True):
        file_list.append(item)
        continue
      found_item = glob.glob(item)
      if (found_item != []):
        file_list=file_list+glob.glob(item)
    return copy.deepcopy(file_list)


  ##
  # @brief trim build env( ex; m_Output, m_Build_Env ..) to ABS(absolute) path
  #        this is for removing the duplications
  # @param bd_ctx[IN]       build context
  # @param bd_ctx_env[OUT]  the output env data to get 
  #                           ex) bd_ctx.m_Build_Env,bd_ctx.m_Output ...
  # @param taglist[IN]      Tags to apply
  #                           ex) [ 'lib_src','swit_src','swut_src','src']
  #
  # @return 
  def Set_Trim_to_ABS_path(self,bd_ctx = None,bd_ctx_env = None ,\
      taglist = None):
    if (taglist == None) :
      taglist = ['inc_path','lib_path','lib_src','src','swit_src','swut_src',\
      'test_inc_path','test_lib_path','bin_file']
    if (bd_ctx == None):
      bd_ctx = self
    if (bd_ctx_env == None):
      bd_ctx_env = bd_ctx.m_Build_Env

    # change file/path list to absolute path
    for idx,item in enumerate(bd_ctx_env): 
      for env_idx,env_val in enumerate(bd_ctx_env[idx][1]): 
         if (env_val[0] in taglist ):
          # in case of 'bin_file' the format is slightly difference
          # ex ) 'inc_path',['inc/x64_Linux_ubuntu']
          # ex ) 'bin_file',[ ['out/x64_Linux_ubuntu/lib/libA.so'],'lib']
           if (env_val[0] == 'bin_file') :
             continue
             #for binfile_idx,binfile_val in enumerate(bd_ctx_env[idx][env_idx][1][1]):
             #  print("\033[1;36m :x: chk "+str(bd_ctx_env[idx][env_idx][1][1][binfile_idx][0])+"\033[m")
             #  bd_ctx_env[idx][env_idx][1][1][binfile_idx][0] = \
             #    bd_ctx.Get_ABS_path(\
             #    [bd_ctx_env[idx][env_idx][1][1][binfile_idx][0]])
           else :
             bd_ctx_env[idx][1][env_idx][1] = \
                 bd_ctx.Get_ABS_path(env_val[1])
             tmp_set = set(bd_ctx_env[idx][1][env_idx][1])
             bd_ctx_env[idx][1][env_idx][1] = list(tmp_set)

    return None


  
  ##
  # @brief Get actual file names list from environment value
  # @param bd_ctx[IN]       build context
  # @param bd_ctx_env[OUT]  the output env data to get 
  #                           ex) bd_ctx.m_Build_Env,bd_ctx.m_Output ...
  # @param taglist[IN]      Tags to apply
  #                           ex) [ 'lib_src','swit_src','swut_src','src']
  #
  # @return 
  def Set_Filelist_from_env_wildcard(self,bd_ctx = None ,bd_ctx_env = None,
      taglist = None):
    if (taglist == None) :
      taglist = [ 'lib_src','swit_src','swut_src','src']
    if (bd_ctx == None):
      bd_ctx = self
    if (bd_ctx_env == None):
      bd_ctx_env = bd_ctx.m_Build_Env

    # change file list from glob wild card
    for idx,item in enumerate(bd_ctx_env): 
      for env_idx,env_val in enumerate(bd_ctx_env[idx][1]): 
         if (env_val[0] in taglist ):
          # in case of 'bin_file' the format is slightly difference
          # ex ) 'inc_path',['inc/x64_Linux_ubuntu']
          # ex ) 'bin_file',[ ['out/x64_Linux_ubuntu/lib/libA.so'],'lib']
           if (env_val[0] == 'bin_file') :
             continue
             #for binfile_idx,binfile_val in enumerate(bd_ctx_env[idx][1][env_idx][1]):
             #  bd_ctx_env[idx][1][env_idx][1][binfile_idx][0] = \
             #    bd_ctx.Get_files_from_wildcard(\
             #    [bd_ctx_env[idx][1][env_idx][1][binfile_idx][0]])
           else :
             bd_ctx_env[idx][1][env_idx][1] = \
                 bd_ctx.Get_files_from_wildcard(env_val[1])


    return

  ##
  # @brief ex) Get_compile_option_list(
  #               '-L',bd_ctx.Get_bd_env_val(bd_env,'lib_path'))
  #         add prefix on each item on the list
  #
  # @param prefix
  # @param option_list
  #
  # @return 
  def Get_compile_option_list(self,prefix,option_list):
    output_list = []
    for item in option_list:
      output_list.append(prefix+item)
    return copy.deepcopy(output_list)

  def Do_dependent_module_build(self,target_config,ModuleCtx):
    dependency_module_info = ModuleCtx.m_Dependency_Module_Info

    top_path= ModuleCtx.m_ModuleID.GetTopPath()

    ret = True
    for module_item in dependency_module_info:
      module_id = ModuleID(module_item[0])
      print("\033[1;32mBuild dependent module:"+str(module_id.m_ModuleID)+\
          "\033[m")
      path=module_id.GetModulePath()
      submodule_config = self.Get_dependency_module_config(ModuleCtx, \
        module_id,target_config)
      cmd ="cd "+top_path+path+' ; '+'scons CONFIG='+submodule_config
      print("\033[1;36mBuild script["+str(cmd)+"] \033[m")

      output=subprocess.call (cmd, shell=True)
      if (output !=0):
        ret = False
        print("\033[1;31mBuild Error on ["+str(module_id.m_ModuleID)+"]\033[m");
      else:
        print("\033[1;32mBuild Done;["+str(module_id.m_ModuleID)+"]\033[m");
    return ret

  def Do_PurgeAll(self,arglist,bd_ctx):
    dependency_module_info = bd_ctx.m_Dependency_Module_Info
    top_path= bd_ctx.m_ModuleID.GetTopPath()
    if type(arglist) is not list:
        return (False,None)

    for key, val in arglist:
      if (key == 'PURGE_ALL'):
        if (val == '1'):
          print("\033[1;31mPurge all includings & its submodules \033[m")
          print("\033[1;36m :x: top_path ; "+str(top_path)+"\033[m")

          ret = bd_ctx.Get_all_dependent_module(bd_ctx.m_Target_Config)
          if (ret[0] == False):
            print("\033[1;31mFail to get submodule lists\033[m")
          dependency_module_list = ret[1]
          for module_item in dependency_module_list:
            module_id = ModuleID(module_item[0])
            print("\033[1;32mPurge dependent module:"+str(module_id.m_ModuleID)+"\033[m")
            path=module_id.GetModulePath()
            # remove each 'out' directory all
            cmd ="cd "+top_path+path+";scons -c; cd - ;"+"rm -r "+top_path+path+DEF_DEFAULT_OUT_PATH 
            print("\033[1;36mPurge script["+str(cmd)+"] \033[m")
            output=subprocess.call (cmd, shell=True)
            if (output !=0):
              print("\033[1;31mPurge Error on ["+str(module_id.m_ModuleID)+"]\033[m");
            else:
              print("\033[1;32mPurge Done;["+str(module_id.m_ModuleID)+"]\033[m");
          # purge self
          print("\033[1;32mPurge module itself:"+str(bd_ctx.m_ModuleID.m_ModuleID)+"\033[m")
          path = bd_ctx.m_ModuleID.GetModulePath()
          # remove each 'out' directory all
          cmd ="cd "+top_path+path+";scons -c; cd - ;"+"rm -r "+top_path+path+DEF_DEFAULT_OUT_PATH 
          print("\033[1;36mPurge script["+str(cmd)+"] \033[m")
          output=subprocess.call (cmd, shell=True)
          if (output !=0):
            print("\033[1;31mPurge Error on ["+str(bd_ctx.m_ModuleID.m_ModuleID)+"]\033[m");
          else:
            print("\033[1;32mPurge Done;["+str(bd_ctx.m_ModuleID.m_ModuleID)+"]\033[m");

          return True
    return False
  
  def Is_Direct_Linking(self,bd_ctx,config):
    direct_linking = 'False'
    env = bd_ctx.Get_config_bd_env(bd_ctx.m_Build_Env,config) 
    direct_linking = bd_ctx.Get_bd_env_val(env,'direct_linking')
    if ( direct_linking ==[] ):
      direct_linking = 'False'
    return direct_linking
  ##
  # @brief Read Output value context
  #
  # @return 
  def Read_Output_Ctx(self,module_inst = None):
    if (module_inst == None):
      ret = Get_ext_Module_inst(self.m_ctx_path,self.m_setting_base_file,
          self.m_ModuleID)
      module_inst = ret[1]

    self.m_Output_Common  = copy.deepcopy(module_inst.Get_output_common())
    self.m_Output_Specific  = copy.deepcopy(module_inst.Get_output_specific())

    # Get output build environment values from merging 
    self.m_Output= copy.deepcopy(module_inst.Get_output_specific())
    for config_idx, config_env in enumerate(self.m_Output): 
      self.m_Output[config_idx][1] = copy.deepcopy(\
              self.merge_items( config_env[1],module_inst.Get_output_common()) )
    
    ## if 'direct_link' option is True, lib_src value should be added to output
    direct_linking = None
    for config_idx, config_env in enumerate(self.m_Output): 
      config = config_env[0]
      env = self.Get_config_bd_env(self.m_Build_Env,config) 
      direct_linking = self.Get_bd_env_val(env,'direct_linking')

      # get lib_src, inc_path from build env
      lib_src = self.Get_bd_env_val(env,'lib_src')
      inc_path = self.Get_bd_env_val(env,'inc_path')
      if (direct_linking == 'True'):
        merge_item = [
              ['inc_path',inc_path],
              ['lib_src',lib_src],
            ]
        # add lib_src & lib_src value to output
        self.m_Output[config_idx][1] = copy.deepcopy(\
              self.merge_items( config_env[1],merge_item) )
        # remove lib ; direct linking doesn't need lib
        for env_idx,env_val in enumerate(self.m_Output[config_idx][1]): 
          if (env_val[0] == 'lib') :
            # remove 'lib' value 
            self.m_Output[config_idx][1][env_idx][1] =[]

    
    # Add the module directory path on output values ;
    # ex) ['inc_path', ['inc/x64_Windows', 'inc']
    #     --> ['inc_path', ['../../Support_Repo/Module_F/inc/x64_Windows', 
    #            '../../Support_Repo/Module_F/inc']
    for idx,item in enumerate(self.m_Output): 
      base_item = self.m_Output[idx]
      for env_idx,env_val in enumerate(base_item[1]): 
        base_env_val = base_item[1][env_idx][1]
        if (env_val[0] == 'inc_path' or 
            env_val[0] == 'bin_file' or
            env_val[0] == 'lib_path' or
            env_val[0] == 'lib_src' 
              ) :
          for val_idx,val_item in enumerate(base_env_val):
            base_val_item = base_env_val
            if (env_val[0] == 'bin_file') :
              # in case of 'bin_file' the format is slightly difference
              # ex ) 'inc_path',['inc/x64_Linux_ubuntu']
              # ex ) 'bin_file',[ [['out/x64_Linux_ubuntu/lib/libA.so'],'lib']
              base_val_item[val_idx][0] =copy.deepcopy(self.m_ModuleID.GetTopPath() \
                +self.m_ModuleID.GetModulePath()+base_val_item[val_idx][0] )
            else :
              base_val_item[val_idx] =copy.deepcopy(self.m_ModuleID.GetTopPath() \
                +self.m_ModuleID.GetModulePath()+base_val_item[val_idx] )

    # Apply(merge) dependency modules' 
    # 'bin_file' , 'lib_path','lib','lib_src' values
    for idx,Build_Env_each_config in enumerate(self.m_Output) :
      output_env_config = Build_Env_each_config[0]
      output_env_val = copy.deepcopy(Build_Env_each_config[1])
      for dependency_module_item in self.m_Dependency_Module:
        connected_config = self.Get_dependency_module_config(
            self,dependency_module_item.m_ModuleID,output_env_config)
        for output_item in dependency_module_item.m_Output:
          if (output_item[0] == connected_config ) :
            output_env_val =copy.deepcopy(output_item[1])
            self.m_Output[idx][1] = \
              copy.deepcopy(self.merge_items(\
              self.m_Output[idx][1],output_env_val,'bin_file'))
            output_env_val =copy.deepcopy(output_item[1])
            self.m_Output[idx][1] = \
              copy.deepcopy(self.merge_items(\
              self.m_Output[idx][1],output_env_val,'lib_path'))
            self.m_Output[idx][1] = \
              copy.deepcopy(self.merge_items(\
              self.m_Output[idx][1],output_env_val,'lib'))
            self.m_Output[idx][1] = \
              copy.deepcopy(self.merge_items(\
              self.m_Output[idx][1],output_env_val,'lib_src'))





  ##
  # @brief copy 'bin_file' to local directory
  #
  # @param config[IN]    copy files' config
  # @param ModuleCtx[IN]
  #
  # @return 
  def Collect_all_dependency_bin_file_list(self,config,ModuleCtx = None) :

    if (ModuleCtx == None):
      ModuleCtx = self
    
    print("\033[1;33mCollect the Module ["+ModuleCtx.m_ModuleID.m_ModuleName \
        +"]'s dependency files \033[m")
    # Get all dependcy module info
    ret = ModuleCtx.Get_all_dependent_module(config)

    # Get config's output context
    output_ctx =ModuleCtx.Get_config_bd_env(ModuleCtx.m_Output,config)
    # Get tag 'bin_file' data from output ctx
    bin_file_info = ModuleCtx.Get_bd_env_val (output_ctx,'bin_file')

    # get bin_file list
    for fileinfo in bin_file_info:
      sourcefile_info = fileinfo[0]
      sourcefile_list = self.Get_files_from_wildcard([sourcefile_info])
      relative_target_path = fileinfo[1]
      local_target_path = DEF_DEFAULT_OUT_PATH +'/'+config+'/'+relative_target_path
      if (os.path.isdir(local_target_path) == False) :
        print("\033[1;32mThe path ["+str(local_target_path)+"] is not existed"+\
            " now generate it\033[m")
        os.makedirs(local_target_path)

      # copy files to local target_path
      for src_file in sourcefile_list:
        # check source file
        if (os.path.isfile(src_file) == False):
          print("\033[1;31msourcefile["+str(src_file)+"] is not existed\033[m")
          continue
        target_file_name_path = local_target_path+'/'+os.path.basename(src_file)
        # if the target file is not exited, copy the source file
        if (os.path.isfile(target_file_name_path) == False) :
          print("\033[1;32mcopy file from ["+str(src_file)+"] to ["\
              +str(local_target_path)+']'\
              +"\033[m")
          shutil.copy(src_file,local_target_path)
        else :
          print("\033[1;31mthe module ["+ModuleCtx.m_ModuleID.m_ModuleName \
              +"] already has the file [" \
              +str(target_file_name_path)+"]\033[m")

  def ReadModuleCtx(self):
    if (self.m_ctx_path == None  
        or self.m_setting_base_file == None 
        or self.m_config_base_file == None):

      print("\033[1;31m  Err; Readmodule Arg err "+str(self.m_ctx_path)+" "+
          str(self.m_setting_base_file)+" "+
          str(self.m_config_base_file)+" "+
          "\033[m\n")
      return False

    # Read Module Settings Context
    ret = Get_ext_Module_inst(self.m_ctx_path,self.m_setting_base_file,
        self.m_ModuleID)
    module_inst = ret[1]

    self.m_Dependency_Module_Info = \
        copy.deepcopy(module_inst.Get_dependency_module_info())

    self.m_Build_Env_Common = copy.deepcopy(module_inst.Get_common_bd_env())
    self.m_Build_Env_Specific= copy.deepcopy(module_inst.Get_specific_bd_env())

    # Get build environment values from merging 
    self.m_Build_Env= copy.deepcopy(module_inst.Get_specific_bd_env())
    for config_env in self.m_Build_Env:
      config_env[1] = copy.deepcopy( self.merge_items( config_env[1], 
        module_inst.Get_common_bd_env()) )

    self.m_Output_Dir  = copy.deepcopy(module_inst.Get_output_dirs())
    self.m_PreBuildJob  = copy.deepcopy(module_inst.Do_pre_build)
    self.m_PostBuildJob  = copy.deepcopy(module_inst.Do_post_build)
   
    # Read Module Config Context
    ret = Get_ext_Module_inst(self.m_ctx_path,self.m_config_base_file,
        self.m_ModuleID)
    module_inst = ret[1]
    self.m_Config_Dictionary = copy.deepcopy(module_inst.Get_CONFIG_DIC())
    
    # create dependency module instance
    for item in self.m_Dependency_Module_Info:
      dependency_module_id = item[0]
      self.m_Dependency_Module.append(ModuleCtx(ModuleID(dependency_module_id)))

    # applying dependency module build info to build environment
    for idx,Build_Env_each_config in enumerate(self.m_Build_Env) :
      build_env_config = Build_Env_each_config[0]
      build_env_val = copy.deepcopy(Build_Env_each_config[1])
      for dependency_module_item in self.m_Dependency_Module:
        connected_config = self.Get_dependency_module_config(
            self,dependency_module_item.m_ModuleID,build_env_config)
        for output_item in dependency_module_item.m_Output:
          if (output_item[0] == connected_config ) :
            output_env_val =copy.deepcopy(output_item[1])
            self.m_Build_Env[idx][1] = \
              copy.deepcopy(self.merge_items(self.m_Build_Env[idx][1],output_env_val))

    # Set Target Binary name  
    for item in self.m_Build_Env:
      target_bin_name = self.Get_bd_env_val(item[1],'target_bin_name')
      if (target_bin_name == []) :
        if ('PROGSUFFIX' in self.m_Config_Dictionary[item[0]]):
          self.m_Target_EXE_file[item[0]] =self.m_ModuleID.m_ModuleName+\
            self.m_Config_Dictionary[item[0]]['PROGSUFFIX']
        else :
          self.m_Target_EXE_file[item[0]] =self.m_ModuleID.m_ModuleName
      else :
        self.m_Target_EXE_file[item[0]] = target_bin_name

      self.m_SWUT_RUNNER_file[item[0]] = 'bin/swut_'+ \
        self.m_Target_EXE_file[item[0]]
      self.m_SWIT_RUNNER_file[item[0]] = 'bin/swit_'+ \
        self.m_Target_EXE_file[item[0]]

      self.m_Target_EXE_file[item[0]] = 'bin/'+self.m_Target_EXE_file[item[0]]

    # Set Target Lib name  
    target_lib_name =[]
    for item in self.m_Build_Env:
      target_lib_name = self.Get_bd_env_val(item[1],'target_lib_name')
      target_config = item[0] # config

      if (target_lib_name == []) :
        target_lib_name =self.m_ModuleID.m_ModuleName

      self.m_Target_Name[target_config] = target_lib_name

      if (self.Get_bd_env_val(item[1],'lib_type') == 'Shared') :
        self.m_Target_LIB_file[item[0]] ='lib/' \
          +self.m_Config_Dictionary[item[0]]['SHLIBPREFIX'] \
          +target_lib_name \
          +self.m_Config_Dictionary[item[0]]['SHLIBSUFFIX']
      elif (self.Get_bd_env_val(item[1],'lib_type') == 'Static') :
        self.m_Target_LIB_file[item[0]] ='lib/'+'lib' \
            +target_lib_name+'.a'

    # Read output context
    self.Read_Output_Ctx()

    return True

  ##
  # @brief Selection of Target CONFIG
  #
  # @param arglist[IN]         arguments 
  #                            ex) [([ ('CONFIG','x64_Windows'),('Opt','00') ]
  # @param default_config[IN]  default build config
  # @param config_dic[IN]      configurations dic
  #
  # @return (True/False,config)   target configuration
  def Get_target_config(self,arglist,default_config=None,config_dic=None):
    if type(arglist) is not list:
        return (False,None)

    if (default_config == None):
      default_config = self.m_Default_Config
    
    if (config_dic == None):
      config_dic = self.m_Config_Dictionary

    if (config_dic == None or default_config == None) :
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
    
    print('target CONFIG selected : '+TARGET_CONFIG)
    return (True,TARGET_CONFIG)

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
  def Get_dependent_module(self,sub_module_info=None): 

    if (sub_module_info == None):
      sub_module_info=self.m_Dependency_Module_Info

    dependency_module_list =[]
    if (sub_module_info == [[]]):
      return dependency_module_list
    for dependency_module in sub_module_info:
      dependency_module_list.append(dependency_module[0])
    return dependency_module_list 


    
  ##
  # @brief Get all dependent module list recursively
  #        the list contains its all sub's dependent contents
  #        directories recursively
  # @param config[IN]       top path of the modules
  #
  # @return (True/False, list of the dependency modules)
  def Get_all_dependent_module(self,config=None):
    dependency_module_list = []
    if (self.m_Dependency_Module_Info !=  None):
      for item in self.m_Dependency_Module:
        # Get the linked taget config
        for info in self.m_Dependency_Module_Info :
          if (info[0] == item.m_ModuleID.m_ModuleID) :
            target_config = info[1][config]
        dependency_module_list.append( 
            [ item.m_ModuleID.m_ModuleID ,target_config] 
            )
        ret =item.Get_all_dependent_module(target_config)
        if (ret[0] == True   # Return should be True
            and ret[1] != [] # not a empty one
            ) :     
          if ( (ret[1] in dependency_module_list) == False):
            dependency_module_list+=ret[1]
    return (True,dependency_module_list)
    
 

  ##
  # @brief Get config's build environment values
  #
  # @param bd_env[IN] total build env
  #  ex) ['x64_Linux_ubuntu', [['inc_path', ['inc', 'libsrc', 'src']], 
  #        ['lib_path', ['lib']], ['lib', ['pthread']], 
  #        ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
  #        ['lib_type', 'Shared'], ['swit_src', ['testframework/swit/*.cpp']], 
  #        ['swut_src', ['testframework/swut/*.cpp']], ['test_lib', ['gtest']], 
  #        ['test_inc_path', ['/home/t0/gtest/googletest/include']], 
  #        ['test_lib_path', ['/home/t0/gtest/googletest/mybuild']], 
  #        ['cppflags', []], ['cflags', []], ['ccflags', []]]], 
  #      ['x64_Windows', [['inc_path', ['inc', 'libsrc', 'src']], 
  #        ['lib_path', ['lib']], ['lib', ['pthread']], 
  #           .....
  # @param config[IN] config to find
  #
  # @return build envrionment value list
  #  ex)
  #      [['inc_path', ['inc', 'libsrc', 'src']], 
  #        ['lib_path', ['lib']], ['lib', ['pthread']], 
  #        ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
  #        ['lib_type', 'Shared'], ['swit_src', ['testframework/swit/*.cpp']], 
  #        ...
  def Get_config_bd_env(self,bd_env,config):
    bd_env = (item for item in bd_env if item[0] == config)
    config_bd_env = None
    cnt =0
    for item in bd_env:
      config_bd_env = copy.deepcopy(item[1])
      cnt +=1
    if (cnt != 1):
      print("\033[1;31mErr; Can not find build env values or duplication"+
          " cnt = "+str(cnt)+" "+
          "\033[m")
      raise CtxInitErr
    return config_bd_env

  def Get_bd_env(self,bd_ctx,config,tag):
    env = self.Get_config_bd_env(bd_ctx.m_Build_Env,config)
    val = self.Get_bd_env_val(env,tag)
    return val

  ##
  # @brief Get build env value from tag
  #     
  #
  # @param bd_env[IN]
  #     ex)
  #      [['inc_path', ['inc', 'libsrc', 'src']], 
  #        ['lib_path', ['lib']], ['lib', ['pthread']], 
  #        ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
  #        ['lib_type', 'Shared'], ['swit_src', ['testframework/swit/*.cpp']], 
  #        ...
  # @param tag[IN] (ex ; 'inc_path','lib_src','cflags'..)
  #
  # @return environment value
  #        ex)  ['inc', 'libsrc', 'src']
  def Get_bd_env_val(self,bd_env,tag):
    env = (item for item in bd_env if item[0] == tag)
    env_val = []
    cnt =0
    for item in env:
      env_val = copy.deepcopy(item[1])
      cnt +=1
    if (cnt > 1):
      print("\033[1;31mErr; tag duplication occured"+
          " tag = "+str(tag)+" "+
          "\033[m")
      raise CtxInitErr
    return env_val
 
  ##
  # @brief Set build context in info on scons builder's 
  #
  # @param bd_ctx[IN] build context
  # @param config[IN] config to set
  # @param builder[OUT] scons builder
  #
  # @return 
  def Set_scons_builder(self,bd_ctx,config,builder):
    print("\033[1;33mModuleID  ; "+str(self.m_ModuleID.m_ModuleID)+"\033[m")
    # change file list from glob wild card
    self.Set_Filelist_from_env_wildcard(bd_ctx,bd_ctx.m_Build_Env)

    # change file/path to absolute path and remove its duplication
    self.Set_Trim_to_ABS_path(bd_ctx,bd_ctx.m_Build_Env)

    #print("\033[1;36mBuild_Env ; "+str(self.m_Build_Env)+"\033[m")

    # set the config data
    config_dic = bd_ctx.m_Config_Dictionary[config]
    for key in config_dic:
      builder[key] = config_dic[key]
    bd_env = self.Get_config_bd_env(bd_ctx.m_Build_Env,config)

    builder.Append(CCFLAGS = \
        self.Get_compile_option_list \
        ('-I',bd_ctx.Get_bd_env_val(bd_env,'inc_path')))

    builder.Append(CFLAGS  =     bd_ctx.Get_bd_env_val(bd_env,'cflags') )
    builder.Append(CPPFLAGS=     bd_ctx.Get_bd_env_val(bd_env,'cppflags'))
    builder.Append(CCFLAGS =     bd_ctx.Get_bd_env_val(bd_env,'ccflags'))
    builder.Append(CXXFLAGS=     bd_ctx.Get_bd_env_val(bd_env,'cxxflags'))
    builder.Append(LIBS    =     bd_ctx.Get_bd_env_val(bd_env,'lib'))
    builder.Append(LINKFLAGS=     bd_ctx.Get_bd_env_val(bd_env,'linkflags'))

    builder.Append(LINKFLAGS = \
        self.Get_compile_option_list\
        ('-L',bd_ctx.Get_bd_env_val(bd_env,'lib_path')))

    # Add depedency modules' output info
    for module_inst in self.m_Dependency_Module:
      connected_config = self.Get_dependency_module_config(self,
          module_inst.m_ModuleID, config)
    
    return

  ##
  # @brief Set build context for scons test builder's 
  #        test builder is for unit test/iteg. test runner build
  # @param bd_ctx[IN] build context
  # @param config[IN] config to set
  # @param builder[OUT] scons builder
  #
  def Set_scons_test_builder(self,bd_ctx,config,builder):
    
    bd_env = self.Get_config_bd_env(bd_ctx.m_Build_Env,config)
    builder.Append(CCFLAGS = \
        self.Get_compile_option_list \
        ('-I',bd_ctx.Get_bd_env_val(bd_env,'test_inc_path')))

    builder.Prepend(LIBS   =     bd_ctx.Get_bd_env_val(bd_env,'test_lib'))
    builder.Prepend(LIBS   =     bd_ctx.m_Target_Name[config])

    builder.Append(LINKFLAGS = \
        self.Get_compile_option_list \
        ('-L',bd_ctx.Get_bd_env_val(bd_env,'test_lib_path')))
    return

  def Make_dirs(self,target_config, dirs,out_dir='./out'):
    for item in dirs:
      dirpath=out_dir+'/'+target_config+'/'+item
      if os.path.isdir(dirpath)==False :
       	os.makedirs(dirpath)

  ##
  # @brief Get dependency module's connected config
  #
  # @param module_ctx[IN]  the instance of ModuleCtx
  # @param dependency_module_id[IN] ex)ModuleID(['Module_B','MainPrj_Repo'])
  # @param config[IN] ex) 'x64_Windows'
  #
  # @return if find it ,this function returns its config 
  def Get_dependency_module_config(self,module_ctx,dependency_module_id,config):
    for item in module_ctx.m_Dependency_Module_Info :
      if (item[0] == dependency_module_id.m_ModuleID) :
        if ( config in item[1] ):
          return item[1][config]
    return None
    
  def Do_Chk_collect_flag(self,arglist,bd_ctx):
    for key, val in arglist:
      if (key == 'COLLECT' and val == '1'):
        bd_ctx.Set_Collect_Flag(True)

  def Set_Collect_Flag(self,collect_flag):
    self.m_Collect_flag = collect_flag

  def Get_Collect_Flag(self):
    return self.m_Collect_flag


  def __del__(self):
    return

def Create_Bd_Ctx(ModuleID = None, 
    top_path = '../../',
    ctx_path = 'build_context/',
    settings_file = 'bd_settings.py',
    config_file = 'bd_config.py'
    ):
  try:
    module_ctx = ModuleCtx(ModuleID)

  except CtxInitErr as e:
    print(e)
    return None
  return module_ctx

def Get_target_config(arglist,default_config=None,config_dic=None,
    config_base_file=None):
  global g_ModuleCtx
  g_ModuleCtx.Get_target_config(arglist,default_config,config_dic,
      config_base_file)
  return


##
# @brief Get Build fail message as str format
#
# @param bf
#
# @return 
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

##
# @brief Get build status
#
# @return 
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


##
# @brief display build status and execution of post build job
#
# @param bd_ctx
# @param target_config
#
# @return 
def display_build_status(bd_ctx,target_config):
  #Display the build status. Called by atexit.              
  #Here you could do all kinds of complicated things       
  status, failures_message = build_status()                   
  if status == 'failed':                                      
    print ("FAILED!!!!") # could display alert, ring bell, etc.
  elif status == 'ok':                                        
    print("\033[1;33mBuild succeeded.\033[m")
    # collect dependency bin files to local directory
    if (bd_ctx.Get_Collect_Flag() == True):
      bd_ctx.Collect_all_dependency_bin_file_list(target_config)

    try :
      bd_ctx.m_PostBuildJob(target_config)
    except NameError :
      print("\033[1;31mNo Post build function\033[m")
  print (failures_message)

