#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main()
{

	char command_config[]="i2cset -y 0 0x44 0x00 0xe539 w";//16 samples, only shunt sampling
	char command_it[]="i2cget -y 0 0x44 0x01 w";
	char command_vt[]="i2cget -y 0 0x44 0x02 w";
	struct timespec now1,now2,start;
	long long diff1,diff2;


	system(command_config);
	clock_gettime(CLOCK_MONOTONIC, &start);
	clock_gettime(CLOCK_MONOTONIC, &now1);

	printf("#start of the time (sec): %lld\n", (long long) start.tv_sec);
	while (1)
	{
		printf("%lld.%.9ld\n", (long long) now1.tv_sec-start.tv_sec, now1.tv_nsec);
		system(command_it);
		printf("0x0000\n");//assuming the voltage is constant
		//system(command_vt);
		fflush(stdout);
		clock_gettime(CLOCK_MONOTONIC, &now2);
		diff1=now2.tv_nsec-now1.tv_nsec;
		if (diff1<0) diff1+=1000000000;
		//printf("%lld\n", (diff1/1000000));
		if (diff1<10000000)
			usleep(10000-(diff1/1000));
		clock_gettime(CLOCK_MONOTONIC, &now2);
		diff1=now2.tv_nsec-now1.tv_nsec;
		if (diff1<0) diff1+=1000000000;
		printf("%lld\n", (diff1/1000000));
		now1=now2;
	}

	return 0;

}
