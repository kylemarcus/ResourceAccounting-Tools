#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>

#define FILENAME_SIZE 64 
#define BUSYBOX_BIN "/data/local/busybox/"

int format_time_string(char *, size_t);

int main()
{

double last,now;
// Create log file
char sched_log_filename[FILENAME_SIZE] = "log/log_";
char line[255];
char * dummy;
int seek,done_line,len,linecount;
char ch;
struct timespec stamp1, stamp2;
long long time1,time2;
double diff;
int rc = format_time_string(&sched_log_filename[8], FILENAME_SIZE);
sprintf(&sched_log_filename[8+rc], "_sched.log");
FILE * log_file = fopen(sched_log_filename,"w");
FILE * fread;
if (log_file == NULL)
{
   perror("ERROR creating sched log");
   exit(EXIT_FAILURE);
}
printf("Created sched log file: %s\n", sched_log_filename);

system("echo 0 > /sys/kernel/debug/tracing/tracing_on");
system("echo nop > /sys/kernel/debug/tracing/current_tracer");
system("echo > /sys/kernel/debug/tracing/set_event");
system("echo > /sys/kernel/debug/tracing/trace");
system("echo sched_switch > /sys/kernel/debug/tracing/set_event");
system("echo 1 > /sys/kernel/debug/tracing/tracing_on");


last=0;

while (1)
{
   printf("----------\n");
   clock_gettime(CLOCK_MONOTONIC, &stamp1);
   time1=stamp1.tv_nsec/1000000;
   time1+=stamp1.tv_sec*1000;
   system("cat /sys/kernel/debug/tracing/trace > sched.tmp");
   clock_gettime(CLOCK_MONOTONIC, &stamp2);
   time2=stamp2.tv_nsec/1000000;
   time2+=stamp2.tv_sec*1000;
   
   diff= (time2 - time1);
   printf("cat lasted %.3f seconds\n", diff/1000);
   fread = fopen("sched.tmp", "r");
   if (fread == NULL)
   {
       perror("ERROR opening the file");
       exit(EXIT_FAILURE);
   }
 
   printf("file opened\n");
   linecount=0;
   while (!feof(fread))
   {
      seek=0;
      done_line=0;
      while(!feof(fread)&&done_line==0)
      {
         ch=fgetc(fread);
         if (ch=='\r' || ch=='\n')
         {
            line[seek]=0;
            done_line=1;
         }
         else line[seek++]=ch;
      }
      if (done_line==1)
      {
          len=seek+1;
          if (line[0]!='#')
          {
             seek=0;
             while(seek<len && (ch=line[seek++])==' ');
             while(seek<len && (ch=line[seek++])!=' ');
             while(seek<len && (ch=line[seek++])==' ');
             while(seek<len && (ch=line[seek++])!=' ');
             while(seek<len && (ch=line[seek++])==' ');
             while(seek<len && (ch=line[seek++])!=' ');
             while(seek<len && (ch=line[seek++])==' ');
             now=0;
             now=strtod(&line[seek-1], &dummy);
             if (now>0)
             {
                if (now>last)
                {
                   last=now;
                   fprintf(log_file,"%s\n",line);
                   linecount++;
                }
             }
             else//exception is "      GL updater"           
             {
                //printf(".\nencountering a bad line: \n%s\n",line);
                while(seek<len && (ch=line[seek++])!=' ');
                while(seek<len && (ch=line[seek++])==' ');
                now=0;
                now=strtod(&line[seek-1], &dummy);
                if (now>0)
                {
                   //printf("found the time\n");
                   if (now>last)
                   {
                      last=now;
                      if (memcmp(line,"      GL updater",16)==0) 
                      {
                         //printf("comparison correct. ");
                         line[8]='_';
                         //printf("modified line:\n%s\n",line);
                      }
                      //else printf("comparison incorrect.\n.\n%s\n%c\n%c",line,line[8],line[9]);
                      fprintf(log_file,"%s\n",line);
                      linecount++;
                   }
                }
                else printf("wrong format in line:\n %s\n",line);
             }
          }
      }
   }
   fflush(log_file);
   printf("wrote %d lines to the log file\n",linecount);
   fclose(fread);
   sleep(3);
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
