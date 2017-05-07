#include <stdio.h>
#include "libmodule_d.h"
int main(int argc, char *argv[]) {
  printf("Hello World\n");
  printf("libmodule() = %d\n", testmodule_Module_D());
  return 0;
}
