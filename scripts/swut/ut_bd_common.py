#!/usr/bin/python2
# -*- coding: utf-8 -*- 
import unittest
import os
import sys

sys.path.append('..')
from bd_common import *

# Defines
TEST_MODULE_PATH = os.getcwd() + '/testfixture/MainPrj_Repo/Module_A'

class Bd_Common_Test(unittest.TestCase):
  def setUp(self):
    ## setup ; change current dir
    #self.origin_dir=os.getcwd()  
    #os.chdir(self.origin_dir+'/..')
    return

  def tearDown(self):
    ## teardown ; back to original dir
      #os.chdir(self.origin_dir)

    return

  def test_ModuleID_basic00(self):
    self.assertRaises(CtxInitErr,ModuleID,('err case'))

    testmoduleid00=ModuleID(['ModuleA','GroupA'])
    self.assertEqual(testmoduleid00.m_GroupName,'GroupA')
    self.assertEqual(testmoduleid00.m_ModuleName,'ModuleA')
    self.assertEqual(testmoduleid00.size(),2)

    module_id_copy = testmoduleid00
    self.assertEqual(module_id_copy.m_GroupName,'GroupA')
    self.assertEqual(module_id_copy.m_ModuleName,'ModuleA')

    testmoduleid01=ModuleID(['ModuleB','GroupB'])
    self.assertEqual(testmoduleid01.m_GroupName,'GroupB')
    self.assertEqual(testmoduleid01.m_ModuleName,'ModuleB')

    self.assertEqual(module_id_copy.m_GroupName,'GroupA')
    self.assertEqual(module_id_copy.m_ModuleName,'ModuleA')


  def test_Get_ext_Module_inst(self):
    ret = Get_ext_Module_inst('./testfixture','test_fixture_no_exist.py')
    self.assertEqual((False,None),ret)
    ret = Get_ext_Module_inst('./testfixture', 'bd_settings.py')
    self.assertEqual(True, ret[0])
    self.assertEqual(['Module_A','MainPrj_Repo'], ret[1].Get_Module_ID())
    testModuleID= ModuleID(ret[1].Get_Module_ID())
    ret = Get_ext_Module_inst('./testfixture','bd_settings.py',testModuleID)
    self.assertEqual(ret[0],True)
    self.assertEqual(ret[1].Get_Module_ID()[0],'Module_A')
    self.assertEqual(ret[1].Get_Module_ID()[1],'MainPrj_Repo')
    ret = Get_ext_Module_inst(None,None)
    self.assertEqual(ret[0],False)



class ModuleCtx_Test(unittest.TestCase):
  def setUp(self):
    return

  def tearDown(self):
    return


  def test_merge_items(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    test_ModuleCtx=ModuleCtx()
    merge =test_ModuleCtx.merge_items(
            [
                ['inc_path', ['inc', 'libsrc', 'src']], 
                ['lib_path', ['out/x64_Linux_ubuntu/lib', 'lib']], 
                ['lib', [ ] ], 
                ['lib_src', ['libsrc']], 
                ['src', ['src']],
                ['bin_file',['doc/util.doc']]
            ],
            [
                ['bin_file', ['lib/libfreetype.so.6','lib/libSDL2_ttf.so','doc/LICENSE.freetype.txt','doc/LICENSE.zlib.txt']], 
                ['lib_path', ['out/x64_Linux_ubuntu/lib','lib/sub']], 
                ['inc_path', ['inc','inc/x64_Linux_ubuntu']], 
                ['lib', ['SDL2_ttf']]
            ],
            None)
    self.assertEqual(merge,
                [
                    ['inc_path', ['inc', 'libsrc', 'src', 'inc/x64_Linux_ubuntu']], 
                    ['lib_path', ['out/x64_Linux_ubuntu/lib', 'lib', 'lib/sub']], 
                    ['lib', ['SDL2_ttf']], 
                    ['lib_src', ['libsrc']], 
                    ['src', ['src']], 
                    ['bin_file', ['doc/util.doc', 'lib/libfreetype.so.6', 'lib/libSDL2_ttf.so', 'doc/LICENSE.freetype.txt', 'doc/LICENSE.zlib.txt']]
                ])
    merge =test_ModuleCtx.merge_items(
            [
                ['inc_path', ['inc', 'libsrc', 'src']], 
                ['lib_path', ['out/x64_Linux_ubuntu/lib', 'lib']], 
                ['lib', [ ] ], 
                ['lib_src', ['libsrc']], 
                ['src', ['src']],
                ['bin_file',['doc/util.doc']]
            ],
            [
                ['bin_file', ['lib/libfreetype.so.6', 'lib/libSDL2_ttf.so', 'doc/LICENSE.freetype.txt', 'doc/LICENSE.zlib.txt']], 
                ['lib_path', ['out/x64_Linux_ubuntu/lib','lib/sub']], 
                ['inc_path', ['inc','inc/x64_Linux_ubuntu']], 
                ['lib', ['SDL2_ttf']]
            ],
            'inc_path')
    self.assertEqual(merge,
            [
                ['inc_path', ['inc', 'libsrc', 'src','inc/x64_Linux_ubuntu']], 
                ['lib_path', ['out/x64_Linux_ubuntu/lib', 'lib']], 
                ['lib', [ ] ], 
                ['lib_src', ['libsrc']], 
                ['src', ['src']],
                ['bin_file',['doc/util.doc']]
            ])
    del test_ModuleCtx
    os.chdir(origin_dir)

  def test_Get_files_from_wildcard(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)
    test_ModuleCtx=ModuleCtx()
    output =test_ModuleCtx.Get_files_from_wildcard(['libsrc/*.cpp','libsrc/sub00/*.cpp'])
    print("\033[1;33m :x: output "+str(output)+"\033[m")

    self.assertEqual(output,['libsrc/libsrcA1.cpp', 'libsrc/libsrcA0.cpp', \
        'libsrc/libmodule.cpp', 'libsrc/sub00/sub00_02.cpp', \
        'libsrc/sub00/sub00_01.cpp'])
    del test_ModuleCtx
    os.chdir(origin_dir)
    
  def test_ModuleCtx_const_dest_test(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)
    test_ModuleCtx=ModuleCtx()
    self.assertEqual(test_ModuleCtx.m_ModuleID.m_ModuleName,'Module_A')
    self.assertEqual(test_ModuleCtx.m_ModuleID.m_GroupName,'MainPrj_Repo')
    del test_ModuleCtx
    os.chdir(origin_dir)
    
    self.assertRaises(CtxInitErr,ModuleCtx,(None,'testfixture','bd_settings'))

    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)
    test_ModuleCtx=ModuleCtx(None,TEST_MODULE_PATH+'/'+DEF_DEFAULT_CTX_PATH,
        'bd_settings.py')
    self.assertEqual(test_ModuleCtx.m_ModuleID.m_ModuleName,'Module_A')
    self.assertEqual(test_ModuleCtx.m_ModuleID.m_GroupName,'MainPrj_Repo')
    del test_ModuleCtx
    os.chdir(origin_dir)

    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)
    test_ModuleCtx=ModuleCtx(None,TEST_MODULE_PATH+'/'+DEF_DEFAULT_CTX_PATH,
        'bd_settings.py','bd_config.py')
    self.assertEqual(test_ModuleCtx.m_Default_Config,'x64_Linux_ubuntu')
    del test_ModuleCtx
    os.chdir(origin_dir)

    # wrong case
    self.assertRaises(CtxInitErr,
        ModuleCtx,(None,'testfixture','settings_file_nowhere.py'))
    try :
      ModuleCtx(None,'testfixture','settings_file_nowhere.py')
    except CtxInitErr as e:
      print(e)
      self.assertEqual('build context Initiation Err',str(e))

    self.assertRaises(CtxInitErr,
        ModuleCtx,(None,'testfixture','settings_file_nowhere.py'))

    self.assertRaises(CtxInitErr,
        ModuleCtx,(None,'testfixture','bd_settings.py',
        'config_file_no_where.py'))

    self.assertRaises(CtxInitErr,
        ModuleCtx,(None,'testfixture','bd_settings_wrong.py'))

    self.assertRaises(CtxInitErr,
        ModuleCtx,(None,'testfixture','bd_settings.py',
        'bd_config_wrong.py'))



  def test_ModuleCtx_test(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    test_ModuleCtx = ModuleCtx()
    self.assertEqual('Module_A',test_ModuleCtx.m_ModuleID.m_ModuleName)
    self.assertEqual('MainPrj_Repo',test_ModuleCtx.m_ModuleID.m_GroupName)
    self.assertEqual('x64_Linux_ubuntu',test_ModuleCtx.m_Default_Config)

    self.assertEqual(test_ModuleCtx.m_Dependency_Module_Info,
        [
                [
                    ['Module_B','MainPrj_Repo'],
                    {
                        'x64_Linux_ubuntu':'x64_Linux_ubuntu',
                        'x64_Windows':'x64_Windows',
                    }
                ],
                [
                    ['Module_C','MainPrj_Repo'],
                    {
                        'x64_Linux_ubuntu':'x64_Linux_ubuntu',
                        'x64_Windows':'x64_Windows',
                    }
                ]
 
           ]
        )
 
    del test_ModuleCtx
    os.chdir(origin_dir)

  def test_dependency_list_chk(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    ModuleA_Ctx = ModuleCtx()
    self.assertEqual(['Module_B', 'MainPrj_Repo'],
        ModuleA_Ctx.m_Dependency_Module[0].m_ModuleID.m_ModuleID)
    self.assertEqual(['Module_C', 'MainPrj_Repo'],
        ModuleA_Ctx.m_Dependency_Module[1].m_ModuleID.m_ModuleID)
#    for item in ModuleA_Ctx.m_Dependency_Module:
#      print("\033[1;32m :x: chk "+str(item.m_ModuleID.m_ModuleID)+" "+
#          str(item.m_ModuleID.GetModulePath())+"\033[m")
    del ModuleA_Ctx

    ModuleA_Ctx = ModuleCtx()
    self.assertEqual(['Module_B', 'MainPrj_Repo'],
        ModuleA_Ctx.m_Dependency_Module[0].m_ModuleID.m_ModuleID)
    self.assertEqual(['Module_C', 'MainPrj_Repo'],
        ModuleA_Ctx.m_Dependency_Module[1].m_ModuleID.m_ModuleID)
    del ModuleA_Ctx

    ModuleA_Ctx = ModuleCtx()
    self.assertEqual(['Module_B', 'MainPrj_Repo'],
        ModuleA_Ctx.m_Dependency_Module[0].m_ModuleID.m_ModuleID)
    self.assertEqual(['Module_C', 'MainPrj_Repo'],
        ModuleA_Ctx.m_Dependency_Module[1].m_ModuleID.m_ModuleID)
    del ModuleA_Ctx

    os.chdir(origin_dir)
  def test_Collect_all_dependency_bin_file_list(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    test_ModuleCtx = ModuleCtx()

    test_ModuleCtx.Collect_all_dependency_bin_file_list('x64_Linux_ubuntu',test_ModuleCtx)
    self.assertEqual(
        test_ModuleCtx.Get_all_dependent_module('x64_Linux_ubuntu'),
        (True, [ 
          [ ['Module_B', 'MainPrj_Repo'], 'x64_Linux_ubuntu' ], 
          [ ['Module_C', 'MainPrj_Repo'], 'x64_Linux_ubuntu' ],
          [ ['Module_D', 'MainPrj_Repo'], 'x64_Linux_ubuntu' ]
            ]))

    del test_ModuleCtx
    os.chdir(origin_dir)


  def test_Get_all_dependent_list(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    test_ModuleCtx = ModuleCtx()
#    self.assertEqual(
#        test_ModuleCtx.Get_all_dependent_module(None),
#        (True, [['Module_B', 'MainPrj_Repo'], ['Module_C', 'MainPrj_Repo'],
#          ['Module_D', 'MainPrj_Repo']]))
    self.assertEqual(
        test_ModuleCtx.Get_all_dependent_module('x64_Linux_ubuntu'),
        (True, [ 
          [ ['Module_B', 'MainPrj_Repo'], 'x64_Linux_ubuntu' ], 
          [ ['Module_C', 'MainPrj_Repo'], 'x64_Linux_ubuntu' ],
          [ ['Module_D', 'MainPrj_Repo'], 'x64_Linux_ubuntu' ]
            ]))


    del test_ModuleCtx
    os.chdir(origin_dir)

  def test_Get_dependent_module(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    test_ModuleCtx=ModuleCtx()
    self.assertEqual(test_ModuleCtx.Get_dependent_module(),
      [['Module_B', 'MainPrj_Repo'], ['Module_C', 'MainPrj_Repo']])
    del test_ModuleCtx
 
    # Wrong Case
    test_ModuleCtx=ModuleCtx()
    self.assertEqual(test_ModuleCtx.Get_dependent_module([[]]),[])
    del test_ModuleCtx

    os.chdir(origin_dir)

#  def test_Set_scons_builder(self):
#    origin_dir=os.getcwd()
#    os.chdir(TEST_MODULE_PATH)
#
#    test_ModuleCtx=ModuleCtx()
#    builder =[]
#    test_ModuleCtx.Set_scons_builder(test_ModuleCtx,'x64_Linux_ubuntu',builder)
#    del test_ModuleCtx
#    os.chdir(origin_dir)
#    return

  def test_Get_config_bd_env(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    test_ModuleCtx=ModuleCtx()
    bd_env =[
        ['x64_Linux_ubuntu', [['inc_path', ['inc', 'libsrc', 'src']], 
          ['lib_path', ['lib']], ['lib', ['pthread']], 
          ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
          ['lib_type', 'Shared'], ['swit_src', ['testframework/swit/*.cpp']], 
          ['swut_src', ['testframework/swut/*.cpp']], ['test_lib', ['gtest']], 
          ['test_inc_path', ['/home/t0/gtest/googletest/include']], 
          ['test_lib_path', ['/home/t0/gtest/googletest/mybuild']], 
          ['cppflags', []], ['cflags', []], ['ccflags', []]]], 
        ['x64_Windows', [['inc_path', ['inc', 'libsrc', 'src']], 
          ['lib_path', ['lib']], ['lib', ['pthread']], 
          ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
          ['lib_type', 'Shared'], ['cppflags', []], ['cflags', []], 
          ['ccflags', []]]], 
        ['arm_Android', [['inc_path', ['inc', 'libsrc', 'src']], 
          ['lib_path', ['lib']], ['lib', ['pthread']], 
          ['lib_src', ['libsrc/*.cpp']], ['src', []], ['cppflags', []], 
          ['cflags', []], ['ccflags', []]]]
        ]
    self.assertEqual(
        [['inc_path', ['inc', 'libsrc', 'src']], 
          ['lib_path', ['lib']], ['lib', ['pthread']], 
          ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
          ['lib_type', 'Shared'], ['swit_src', ['testframework/swit/*.cpp']], 
          ['swut_src', ['testframework/swut/*.cpp']], ['test_lib', ['gtest']], 
          ['test_inc_path', ['/home/t0/gtest/googletest/include']], 
          ['test_lib_path', ['/home/t0/gtest/googletest/mybuild']], 
          ['cppflags', []], ['cflags', []], ['ccflags', []]],
        test_ModuleCtx.Get_config_bd_env(bd_env,"x64_Linux_ubuntu"))
    with self.assertRaises(CtxInitErr):
      test_ModuleCtx.Get_config_bd_env(bd_env,"x64_wrong")
      
    os.chdir(origin_dir)

  def test_Get_bd_env_val(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)
    test_ModuleCtx=ModuleCtx()
    bd_env = [['inc_path', ['inc', 'libsrc', 'src']], 
          ['lib_path', ['lib']], ['lib', ['pthread']], 
          ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
          ['lib_type', 'Shared'], ['swit_src', ['testframework/swit/*.cpp']], 
          ['swut_src', ['testframework/swut/*.cpp']], ['test_lib', ['gtest']], 
          ['test_inc_path', ['/home/t0/gtest/googletest/include']], 
          ['test_lib_path', ['/home/t0/gtest/googletest/mybuild']], 
          ['cppflags', []], ['cflags', []], ['ccflags', []]]
    self.assertEqual(
        ['inc', 'libsrc', 'src'], 
        test_ModuleCtx.Get_bd_env_val(bd_env,"inc_path"))
    self.assertEqual(
        ['testframework/swut/*.cpp'], 
        test_ModuleCtx.Get_bd_env_val(bd_env,"swut_src"))

    bd_env = [['inc_path', ['inc', 'libsrc', 'src']], 
          ['lib_path', ['lib']],
          ['lib', ['pthread']],['lib', ['pthread']], # duplication of 'lib'
          ['lib_src', ['libsrc/*.cpp']], ['src', ['src/main.cpp']], 
          ['lib_type', 'Shared'], ['swit_src', ['testframework/swit/*.cpp']], 
          ['swut_src', ['testframework/swut/*.cpp']], ['test_lib', ['gtest']], 
          ['test_inc_path', ['/home/t0/gtest/googletest/include']], 
          ['test_lib_path', ['/home/t0/gtest/googletest/mybuild']], 
          ['cppflags', []], ['cflags', []], ['ccflags', []]]

    with self.assertRaises(CtxInitErr):
      test_ModuleCtx.Get_bd_env_val(bd_env,"lib")
    os.chdir(origin_dir)


  def test_Get_dependecy_module_config(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)
    test_ModuleCtx=ModuleCtx()
    self.assertEqual('x64_Windows',
        test_ModuleCtx.Get_dependency_module_config(
          test_ModuleCtx,ModuleID(['Module_B','MainPrj_Repo']),'x64_Windows'))

    self.assertEqual(None,
        test_ModuleCtx.Get_dependency_module_config(
          test_ModuleCtx,ModuleID(['Module_B','MainPrj_Repo']),'wrong_config'))


    del test_ModuleCtx
    os.chdir(origin_dir)
 
  def test_Get_target_config(self):
    origin_dir=os.getcwd()
    os.chdir(TEST_MODULE_PATH)

    test_ModuleCtx=ModuleCtx()
    self.assertEqual(test_ModuleCtx.Get_target_config(None),(False,None))
    test_Arguments=[ ('CONFIG','x64_Windows'),('Dummy','Dummy') ]
    self.assertEqual(
        test_ModuleCtx.Get_target_config(test_Arguments),
        (True,'x64_Windows'))
    del test_ModuleCtx

    test_ModuleCtx=ModuleCtx()
    self.assertEqual(test_ModuleCtx.Get_target_config(None),(False,None))
    test_Arguments=[ ('CONFIG','x64_Windows'),('Dummy','Dummy') ]
    self.assertEqual(
        (True,'x64_Windows'),
        test_ModuleCtx.Get_target_config(test_Arguments)
        )
    del test_ModuleCtx
 
    test_ModuleCtx=ModuleCtx()
    test_Arguments=[ ('CONFIG','x64_Windows'),('Dummy','Dummy') ]
    self.assertEqual(
        (True,'x64_Windows'),
        test_ModuleCtx.Get_target_config(test_Arguments,'x64_Linux_ubuntu')
        )
    self.assertEqual(
        test_ModuleCtx.Get_target_config(test_Arguments,'x64_Linux_ubuntu','Dummy'),
        (True, 'x64_Linux_ubuntu'))
    del test_ModuleCtx
    
    os.chdir(origin_dir)
    return


if __name__ == "__main__":
  #suite00 = unittest.TestSuite(map(ModuleCtx_Test,['test_Collect_all_dependency_bin_file_list']))
  #suites = unittest.TestSuite([suite00])
  #unittest.TextTestRunner(verbosity=2).run(suites)

  unittest.main()
