#include <stdio.h>
#include "libmodule.h"
int main(int argc, char *argv[])
{
    printf("Hello World\n");
    printf("libmodule() = %d\n",Module_B());
    return 0;
}
