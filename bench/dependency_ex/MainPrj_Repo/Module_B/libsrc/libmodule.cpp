#include "libmodule_d.h"
#include "libmodule_e.h"

int testmodule_Module_B() {
  return testmodule_Module_D()+testmodule_Module_E()+7;
}
