#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <sys/stat.h>
#include <sys/types.h>

#define FILENAME_SIZE 64 
#define LOG_DIR "log"

int format_time_string(char *, size_t);

int main(int argc, const char * argv[])
{

    // Create log directory
    struct stat info;
    if (stat(LOG_DIR, &info) != 0)
    {
        if (mkdir(LOG_DIR, 0777) < 0)
        {
            perror("ERROR mkdir log directory");
            exit(EXIT_FAILURE);
        }
        printf("Created log dir: " LOG_DIR "\n");
    }

    // Create socket log file
    char socket_log_filename[FILENAME_SIZE] = LOG_DIR "/log_";
    int rc = format_time_string(&socket_log_filename[8], FILENAME_SIZE);
    sprintf(&socket_log_filename[8+rc], "_socket.log");
    FILE * sfp = fopen(socket_log_filename,"w");
    if (sfp == NULL)
    {
        perror("ERROR creating socket log");
        exit(EXIT_FAILURE);
    }
    printf("Created socket log file: %s\n", socket_log_filename);

    // Write socket log header
    fprintf(sfp, "#Time\t#0=reqest,1=respond\t#Name\t#PID\n");

    fclose(sfp);

}

int format_time_string(char * buffer, size_t buffer_size)
{
    time_t timer;
    struct tm * tm_info;

    if (time(&timer) < 0)
    {
        perror("ERROR time call");
        exit(EXIT_FAILURE);
    }

    tm_info = localtime(&timer);
    if (tm_info == NULL)
    {
        perror("ERROR localtime call");
        exit(EXIT_FAILURE);
    }

    int rc = strftime(buffer, FILENAME_SIZE-8, "%Y_%m_%d_%H_%M_%S", tm_info);
    if (rc < 0)
    {
        perror("ERROR strftime call");
        exit(EXIT_FAILURE);
    }

    return rc;
}
