#include <stdio.h>
#include "libmodule.h"
extern int Module_B();
extern int ModuleB_Sub00();
extern int ModuleB_Sub01();
int main(int argc, char *argv[])
{
    printf("Hello World\n");
    printf("libmodule() = %d\n",testmodule());
    printf("Module_B() = %d\n",Module_B());
    printf("ModuleB_Sub00() = %d\n",ModuleB_Sub00());
    printf("ModuleB_Sub01() = %d\n",ModuleB_Sub01());
    return 0;
}
