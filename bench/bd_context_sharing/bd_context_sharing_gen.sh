#!/bin/sh
rm -rf build_context
rm -rf MainPrj_Repo Support_Repo
cd ../.. ; ./gen_mobs.sh ; cd -
../../mobs.py Module_A MainPrj_Repo
../../mobs.py Module_B MainPrj_Repo
../../mobs.py Module_C MainPrj_Repo

../../mobs.py Module_D Support_Repo
../../mobs.py Module_E Support_Repo
../../mobs.py Module_F Support_Repo
../../mobs.py Module_G Support_Repo

# make build context files to use commonly
mkdir build_context
cp MainPrj_Repo/Module_A/build_context/bd_config.py build_context
cp MainPrj_Repo/Module_A/build_context/bd_common.py build_context

# remove each build context files to test
rm MainPrj_Repo/Module_A/build_context/bd_config.py
rm MainPrj_Repo/Module_B/build_context/bd_config.py
rm MainPrj_Repo/Module_C/build_context/bd_config.py
rm Support_Repo/Module_D/build_context/bd_config.py
rm Support_Repo/Module_E/build_context/bd_config.py
rm Support_Repo/Module_F/build_context/bd_config.py
rm Support_Repo/Module_G/build_context/bd_config.py

rm MainPrj_Repo/Module_A/build_context/bd_common.py
rm MainPrj_Repo/Module_B/build_context/bd_common.py
rm MainPrj_Repo/Module_C/build_context/bd_common.py
rm Support_Repo/Module_D/build_context/bd_common.py
rm Support_Repo/Module_E/build_context/bd_common.py
rm Support_Repo/Module_F/build_context/bd_common.py
rm Support_Repo/Module_G/build_context/bd_common.py


cd MainPrj_Repo/Module_A ; scons ; cd -
cd MainPrj_Repo/Module_B ; scons ; cd -
cd MainPrj_Repo/Module_C ; scons ; cd -

cd Support_Repo/Module_D ; scons ; cd -
cd Support_Repo/Module_E ; scons ; cd -
cd Support_Repo/Module_F ; scons ; cd -
cd Support_Repo/Module_G ; scons ; cd -
#patch -p0 < MainPrj_Repo.diff
#patch -p0 < Support_Repo.diff
