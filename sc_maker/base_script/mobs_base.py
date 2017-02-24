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


"""+++script_delimeter+++"""


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
