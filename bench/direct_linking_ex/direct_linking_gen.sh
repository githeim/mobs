!/bin/sh
rm -rf MainPrj_Repo 
cd ../.. ; ./gen_mobs.sh ; cd -
../../mobs.py Module_A MainPrj_Repo
../../mobs.py Module_B MainPrj_Repo
../../mobs.py Module_C MainPrj_Repo
../../mobs.py Module_D MainPrj_Repo
../../mobs.py Module_E MainPrj_Repo

patch -p0 < MainPrj_Repo.diff
cd MainPrj_Repo/Module_A ; scons ; cd -
