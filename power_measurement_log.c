#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

int keepRunning = 1;

void intHandler(int dummy) {
    keepRunning = 0;
}

int main()
{

	signal(SIGINT, intHandler);

	char command_it[]="i2cget -y 0 0x44 0x01 w";
	char command_vt[]="i2cget -y 0 0x44 0x02 w";
	char command_ig[]="i2cget -y 0 0x40 0x01 w";
	char command_vg[]="i2cget -y 0 0x40 0x02 w";
	struct timespec now;
	unsigned int microseconds = 10000;

	while (keepRunning)
	{
		clock_gettime(CLOCK_MONOTONIC, &now);
		printf("%lld.%.9ld\n", (long long) now.tv_sec, now.tv_nsec);
		system(command_it);
		system(command_it);
		system(command_ig);
		system(command_vg);
		clock_gettime(CLOCK_MONOTONIC, &now);
		printf("%lld.%.9ld\n", (long long) now.tv_sec, now.tv_nsec);
		fflush(stdout);
		usleep(microseconds);
	}

	return 0;

}
