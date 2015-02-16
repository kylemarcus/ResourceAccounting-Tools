#include <time.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{

	FILE * log = fopen("log/marker.log", "w");

	while(1) {

		printf("Enter 'o' for going outside and 'i' for going inside\n");

		char letter;
		scanf(" %c", &letter);

		struct timespec now;
		clock_gettime(CLOCK_MONOTONIC, &now);

		if (letter == 'i') {

			printf("Going inside at %lld.%.9ld\n", (long long) now.tv_sec, now.tv_nsec);
			fprintf(log, "Going inside at %lld.%.9ld\n", (long long) now.tv_sec, now.tv_nsec);

		}

		else if (letter == 'o') {

			printf("Going outside at %lld.%.9ld\n", (long long) now.tv_sec, now.tv_nsec);
			fprintf(log, "Going outside at %lld.%.9ld\n", (long long) now.tv_sec, now.tv_nsec);

		}

		else {

			printf("Enter command again\n");

		}

		fflush(stdout);
		fflush(log);

	}

}

