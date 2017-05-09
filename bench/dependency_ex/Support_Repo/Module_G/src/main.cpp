#include <stdio.h>
#include "libmodule_g.h"
int main(int argc, char *argv[]) {
  printf("Hello World\n");
  printf("libmodule() = %d\n", testmodule_Module_G());
  return 0;
}
