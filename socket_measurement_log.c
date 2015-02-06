#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define FILENAME_SIZE 64 
#define SOCKET_BUFF_SIZE 1024
#define LOG_DIR "log"
#define PORT_NUM 40000
#define BUSYBOX_BIN "/data/local/busybox/"

int get_process_name_pid(const int, char *, int *);
int format_time_string(char *, size_t);

/*
 * Creates a server that listens for connections from
 * gpsd with info about request and response times.
 * Logs info to socket log files.
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
    fflush(sfp);

    // Create server
    int sockfd, newsockfd, clilen, n;
    char buffer[SOCKET_BUFF_SIZE];
    struct sockaddr_in serv_addr, cli_addr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("ERROR opening socket");
        exit(EXIT_FAILURE);
    }

    // Not available in Android kernel
    /*
    int optval = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, &optval, sizeof(optval)) < 0)
    {
        perror("ERROR setting socket options");
    }
    */

    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(PORT_NUM);

    if (bind(sockfd, (struct sockaddr *) &serv_addr,
                        sizeof(serv_addr)) < 0)
    {
        perror("ERROR on binding");
        exit(EXIT_FAILURE);
    }

    listen(sockfd, 5);
    clilen = sizeof(cli_addr);

    printf("Server listening on port %d\n", PORT_NUM);

    // Server accept loop
    while (1)
    {
        newsockfd = accept(sockfd, (struct sockaddr *)&cli_addr, &clilen);
        if (newsockfd < 0)
        {
            perror("ERROR on accept");
            close(newsockfd);
            continue;
        }
        printf("Server accepted connection\n");

        bzero(buffer, SOCKET_BUFF_SIZE);
        if (read(newsockfd, buffer, SOCKET_BUFF_SIZE) < 0)
        {
            perror("ERROR reading from socket");
            close(newsockfd);
            continue;
        }

        int record_type = 0;
        int process_port = 0;
        int process_tm[2];
        if (sscanf(buffer, "%d|%d|%d.%d", &record_type, &process_port, &process_tm[0], &process_tm[1]) < 0)
        {
            perror("ERROR processing socket data");
            close(newsockfd);
            continue;
        }
        else
        {
            printf("record type: %d, process port: %d\n", record_type, process_port);
        }

        char process_name[32];
        int process_pid = 0;
        if (get_process_name_pid(process_port, process_name, &process_pid) < 0)
        {
            perror("ERROR processing name and pid");
            close(newsockfd);
            continue;
        }

        // Note: 1000000000 ns = 1 second
        double now_time = process_tm[0] + (process_tm[1] / 1000000000.0);
        char str_time[64];
        sprintf(str_time, "%.6f", now_time - reference_time);

        // Write out records to file
        if (fprintf(sfp, "%s -- %d -- %s -- %d\n", str_time, record_type, process_name, process_pid) < 0)
        {
            perror("ERROR writing to socket log");
            close(newsockfd);
            continue;
        }
        fflush(sfp);

        close(newsockfd);
    }
}

/*
 * Gets the PID and process name thats listening on a 
 * specific port number, note that busybox needs
 * to be installed with netstat and awk.
 * NOTE: the PATH env var needs to have buxybox bin included in path
 */
int get_process_name_pid(const int port, char * name, int * pid)
{
    char command[128];
    sprintf(command, BUSYBOX_BIN "netstat -apeen 2>/dev/null | awk '$4~/:%d/ {print $7}'", port);

    FILE * fp = popen(command, "r");
    if (fp == NULL)
    {
        perror("ERROR failed to run netstat command");
        return -1;
    }

    char output[128];
    if (fgets(output, sizeof(output)-1, fp) < 0)
    {
        perror("ERROR getting output from netstat");
        return -1;
    }

    pclose(fp);

    if (sscanf(output, "%d/%s", pid, name) < 0)
    {
        perror("ERROR processing netstat data");
        return -1;
    }

    return 0;
}

/*
 * Formats a time string to a specific format.
 */
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
