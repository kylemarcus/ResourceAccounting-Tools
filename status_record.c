#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main()
{
	char command_i[]="i2cget -y 0 0x44 0x01 w";
	char command_v[]="i2cget -y 0 0x44 0x02 w";

	while (1)
	{
		system(command_i);
		system(command_v);
		fflush(stdout);
		sleep(2);
	}

	return 0;

}
