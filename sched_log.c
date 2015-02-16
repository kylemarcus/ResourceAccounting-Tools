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
int seek,done_line,len;
char ch;
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


system("export TPATH=\"/sys/kernel/debug/tracing\"");
system("echo 0 > $TPATH/tracing_on");
system("echo nop > $TPATH/current_tracer");
system("echo > $TPATH/set_event");
system("echo > $TPATH/trace");
system("echo sched_switch > $TPATH/set_event");
system("echo 1 > $TPATH/tracing_on");


last=0;

while (1)
{
   system("cat /sys/kernel/debug/tracing/trace > log/run_tmp.tmp");
   fread = fopen("log/run_tmp.tmp", "r");

   while (!feof(fread))
   {
      seek=0;
      done_line=0;
      while(!feof(fread)||done_line==0)
      {
         ch=fgetc(fread);
         if (ch=='\r' || ch=='\n')
         {
            line[seek]=0;
            done_line=1;
         }
         else line[seek]=ch;
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
             sscanf(&line[seek], "%f", &now);
             if (now>0)
             {
                printf("got time: %f",now);
                if (now>last)
                {
                   last=now;
                   fprintf(log_file,"%s\n",line);
                }
             }
             else printf("wrong format in line:\n %s",line);
          }
      }
   }
   fflush(log_file);
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
