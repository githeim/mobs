#include <stdio.h>
#include "libmodule_b.h"
int main(int argc, char *argv[]) {
  printf("Hello World\n");
  printf("libmodule() = %d\n", testmodule_Module_B());
  return 0;
}
