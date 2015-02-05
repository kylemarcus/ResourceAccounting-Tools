#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include "user_event_log.h"

#define FILENAME_SIZE 64 
#define LOG_DIR "log"
#define DEV_LOG "/dev/event_log_dev"
#define SLEEP_SEC 15

int format_time_string(char *, int, int);
int get_device(int, char *);
int set_device_info(int, int, char *, struct user_event_log *);

/*
 * Logs info from /dev/event_log_dev into file
 */
int main(int argc, const char * argv[])
{
    double reference_time = 0;

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

    // Create log file
    char eventdevice_log_filename[FILENAME_SIZE] = LOG_DIR "/log_";
    int skip = strlen(eventdevice_log_filename);
    int rc = format_time_string(&eventdevice_log_filename[skip], FILENAME_SIZE, skip);
    sprintf(&eventdevice_log_filename[skip+rc], "_eventdevice.log");
    FILE * edfp = fopen(eventdevice_log_filename,"w");
    if (edfp == NULL)
    {
        perror("ERROR creating eventdevice log");
        exit(EXIT_FAILURE);
    }
    printf("Created eventdevice log file: %s\n", eventdevice_log_filename);

    // Write log header
    fprintf(edfp, "#Name\t#Open-time\t#PID\t#Latency\n");
    fflush(edfp);

    // Open dev
    int dlfd = open(DEV_LOG, O_RDWR);
    if (dlfd < 0)
    {
        perror("ERROR opening event_log_dev");
        exit(EXIT_FAILURE);
    }

    int ndevices = 0;
    int flag = 0;
    unsigned char minors[MAX_INPUT_DEVICE];
    while (ndevices == 0)
    {
        ndevices = get_device(dlfd, minors);
        if (ndevices < 0)
        {
            perror("ERROR get_device");
            exit(EXIT_FAILURE);
        }

        if (flag == 0)
        {
            printf("Wait till gps opens for reading\n");
            flag = 1;
        }
    }
    printf("Devices found: %d\n", ndevices);

    while (1)
    {
        //fprintf(edfp, "DEVICE_NAME\tOPEN_TIME\tPID\tLATENCY");
        
        int dev;
        ndevices = 0;
        // NOTE: bug in ioctl LGETDEVS code that always 
        // increases dev and never decreases so we only
        // look at dev 0 or code will cause kernel panic
        for (dev = 0; dev <= ndevices; dev++)
        {
            struct user_event_log log;
            if (set_device_info(dlfd, dev, minors, &log) < 0)
            {
                perror("ERROR set_device_info");
                continue;
            }

            int i;
            for (i=0; i<log.ncount; i++) {
                fprintf(edfp, "%s \t %ld.%06ld \t %d \t %ld.%06ld \n",
                              log.name, log.dev_opened_time.tv_sec, log.dev_opened_time.tv_usec,
                              log.event_consumed[i].pid, log.avg.tv_sec, log.avg.tv_usec);
            }
            fflush(edfp);
            
            // Not really sure why python module returns inside loop?
        }

        sleep(SLEEP_SEC);
    }
}

int set_device_info(int fd, int dev, char * minors, struct user_event_log * log)
{
    if (minors[dev] == END_MARK)
    {
        perror("ERROR found END_MARK for dev trying to get info");
        return -1;
    }

    struct user_args cargs;
    unsigned int i = 0;
    cargs.minor = dev;
    cargs.p = log;

    if (ioctl(fd, LGETDEVINFO, &cargs) < 0)
    {
        perror("ERROR ioctl LGETDEVINFO");
        return -1;
    }

    return 0;
}

/*
 * Note there seems to be some kind of 
 * error in this ioctl code, the number of
 * devices never decreases and always increases
 * so we are really only concerned with dev 0
 */
int get_device(int fd, char * minors)
{
    int ndevices = 0;
    if (ioctl(fd, LGETDEVS, minors) < 0)
    {
        perror("ERROR ioctl LGETDEVS");
        return -1;
    }

    while (minors[ndevices] != END_MARK)
    {
        ndevices++;
    }

    return ndevices;
}

/*
 * Formats a time string to a specific format, this used
 * to create a time stamp string inside another string for
 * use in a filename. The skip_chars arg is the number of
 * chars that you want to skip at the start of the buffer.
 */
int format_time_string(char * buffer, int buffer_size, int skip_chars)
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

    int rc = strftime(buffer, buffer_size-skip_chars, "%Y_%m_%d_%H_%M_%S", tm_info);
    if (rc < 0)
    {
        perror("ERROR strftime call");
        exit(EXIT_FAILURE);
    }

    return rc;
}
