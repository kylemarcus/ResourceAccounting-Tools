#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main()
{
	char command_it[]="i2cget -y 0 0x44 0x01 w";
	char command_vt[]="i2cget -y 0 0x44 0x02 w";
	struct timespec now1,now2;
	long long diff1,diff2;
	unsigned int microseconds = 10000;

	while (1)
	{
		clock_gettime(CLOCK_MONOTONIC, &now1);
		printf("%lld.%.9ld\n", (long long) now1.tv_sec, now1.tv_nsec);
		system(command_it);
		system(command_vt);
		clock_gettime(CLOCK_MONOTONIC, &now2);
		diff1=now2.tv_nsec-now1.tv_nsec;
		if (diff1<0) diff1+=1000000000;
		printf("%lld\n", (diff1/1000000));
		fflush(stdout);
	}

	return 0;

}
