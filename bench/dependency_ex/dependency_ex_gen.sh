!/bin/sh
rm -rf MainPrj_Repo Support_Repo
cd ../.. ; ./gen_mobs.sh ; cd -
../../mobs.py Module_A MainPrj_Repo
../../mobs.py Module_B MainPrj_Repo
../../mobs.py Module_C MainPrj_Repo

../../mobs.py Module_D Support_Repo
../../mobs.py Module_E Support_Repo
../../mobs.py Module_F Support_Repo
../../mobs.py Module_G Support_Repo
patch -p0 < MainPrj_Repo.diff
patch -p0 < Support_Repo.diff
cd MainPrj_Repo/Module_A ; scons ; cd -
