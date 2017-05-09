#include <stdio.h>
#include "libmodule_c.h"
int main(int argc, char *argv[]) {
  printf("Hello World\n");
  printf("libmodule() = %d\n", testmodule_Module_C());
  return 0;
}
