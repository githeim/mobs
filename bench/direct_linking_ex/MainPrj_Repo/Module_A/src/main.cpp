#include <stdio.h>
#include "libmodule_a.h"
#include "libmodule_b.h"
#include "libmodule_c.h"
int main(int argc, char *argv[]) {
  printf("Hello World\n");
  printf("testmodule_Module_A() = %d\n", testmodule_Module_A());
  printf("testmodule_Module_B() = %d\n", testmodule_Module_B());
  printf("testmodule_Module_C() = %d\n", testmodule_Module_C());
  return 0;
}
