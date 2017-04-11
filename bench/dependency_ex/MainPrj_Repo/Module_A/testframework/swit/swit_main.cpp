#include <gtest/gtest.h>
#include "libmodule.h"
// Test template    

class SampleTest : public testing::Test {
    protected:
        virtual void SetUp() {
        }
        virtual void TearDown() {
        }
};
 
TEST_F(SampleTest, BasicTest00) {
    EXPECT_EQ(2, (1+1));
    EXPECT_EQ(5, (2+3));
    EXPECT_EQ(testmodule(), 7);
}


int main(int argc, char *argv[])
{
    char bus_addr[1024] ={ 0 , };
    char cmd[2048] ={ 0 , };
    int custom_argc=2;
    char* pArgv[2];
    char* pCmd1 =(char*)"--gtest_output=xml:swit_report.xml";
    pArgv[1] = pCmd1;

    ::testing::InitGoogleTest(&custom_argc,(char**)pArgv);
    return RUN_ALL_TESTS();
}
