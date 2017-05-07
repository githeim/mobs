#include <stdio.h>
#include "libmodule.h"
int main(int argc, char *argv[]) {
  printf("Hello World\n");
  printf("libmodule() = %d\n", testmodule_Module_E());
  return 0;
}
