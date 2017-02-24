#!/usr/bin/python3
# -*- coding: utf-8 -*- 
import unittest
import os
import glob

import sys

from sc_maker import *

# the following delimeter will replaced to file scripts functions
g_Script_Delimeter ="\"\"\"+++script_delimeter+++\"\"\""

##
# @brief change file contents to python string
#
# @param filecontents
#
# @return 
def FileContentsChanger(filecontents):
  output =filecontents
  output = output.replace("\\","\\\\")
  return output

##
# @brief change filename to function name style
#         ex) test-file.cpp --> test_file_cpp
#         ex) _ut-file.py --> _ut_file_py
#
# @param filename[IN]
#
# @return 
def FileNameChanger(filename):
  output =filename
  output = output.replace(".","_")
  output = output.replace("-","_")
  return output
##
# @brief change file text to function script
#
# @param filepath[IN] file contents to change
# 
#
# @return sucess (True,script) failed (False,None)

##
# @brief change file text to function script
#
# @param fileText[IN] file's text
# @param fileName[IN] file name
# @param funcNamePrefix[IN] function name prefix 
#
# @return 
def FileText2FuncScript(fileText,fileName,funcNamePrefix="getScript_"):
  fileNameScript= FileNameChanger(fileName) 
  file_contents = FileContentsChanger(fileText)

  output_script="""def """+funcNamePrefix+fileNameScript+"() :\n"
  output_script+="  return \\\n"
  output_script+="\"\"\""+file_contents+"\"\"\"\n"

  return output_script

def Make_Script(TargetScriptName,BaseScript,ScriptFilePath):
  # Get Script file list
  filelist =glob.glob(ScriptFilePath+"/*")
  # Generate Script file contents into one string
  filecontents_text =""
  for file_path in filelist:
    with open (file_path,'r',errors='ignore') as f:
      filetext=f.read()
      filename = os.path.basename(file_path)
      filecontents_text += FileText2FuncScript(filetext,filename)
      


  # Replace delimeter flag to file contents string
  script_output=""
  with open(BaseScript,'r',errors ='ignore') as base_script_fp:
    script_output =base_script_fp.read()
    script_output = script_output.replace(g_Script_Delimeter,filecontents_text)
  script_output
  return script_output


def main(argv): # pragma: no cover
  if (len(argv) != 4):
    print("\033[1;31mhow to use \033[m");
    print("\033[1;32m$ sc_maker pythonscriptname base_script scriptfilepath \033[m\n");
    print("\033[1;32mex) $ sc_maker mobs.py mobs/base_script/mobs_base.py mobs/scripts \033[m\n");
    return False
  output=Make_Script(argv[1],argv[2],argv[3])
  with open (argv[1],'w',errors='ignore') as f:
    f.write(output)
  os.chmod(argv[1],0o700)
  print("\033[1;33mGeneration of script ["+argv[1]+"] is Done \033[m\n");

  return True;
  
if __name__ == "__main__": # pragma: no cover
  main(sys.argv)
