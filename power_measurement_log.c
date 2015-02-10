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

	char command_i[]="i2cget -y 0 0x44 0x01 w";
	char command_v[]="i2cget -y 0 0x44 0x02 w";
	struct timespec now;
	unsigned int microseconds = 10000;

	while (keepRunning)
	{
		clock_gettime(CLOCK_MONOTONIC, &now);
		printf("%lld.%.9ld\n", (long long) now.tv_sec, now.tv_nsec);
		system(command_i);
		system(command_v);
		fflush(stdout);
		usleep(microseconds);
	}

	return 0;

}
