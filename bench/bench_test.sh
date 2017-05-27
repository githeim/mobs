#!/bin/sh
cd bd_context_sharing ;  ./bd_context_sharing_gen.sh; cd -
cd dependency_ex ; ./dependency_ex_gen.sh ; cd -
cd direct_linking_ex ; ./direct_linking_gen.sh ; cd -
