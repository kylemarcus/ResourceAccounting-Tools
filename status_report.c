#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{

double last,now;
char line[255];
char last_line[255];
char current_line[255];
int seek,done_line,len;
char ch;

float voltage,current;
FILE * fread;

last=0;
len=0;
current_line[len]=last_line[len]=line[len]=0;
while (1)
{
   printf("----------\n");
   fread = fopen("status.tmp", "r");
   if (fread == NULL)
   {
       perror("ERROR reading status log");
       exit(EXIT_FAILURE);
   }
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
         strcpy(last_line,current_line);
         strcpy(current_line,line);
      } 
   }
   fclose(fread);
//   printf("read status log file:\n");

   current=0;
   current+=last_line[4]<58?last_line[4]-48:last_line[4]-87;
   current*=16;
   current+=last_line[5]<58?last_line[5]-48:last_line[5]-87;
   current*=16;
   current+=last_line[2]<58?last_line[2]-48:last_line[2]-87;
   current*=16;
   current+=last_line[3]<58?last_line[3]-48:last_line[3]-87;

   current=current/10;
   printf("Current: %s -> %.1f mA\n",last_line,current);

   voltage=0;
   voltage+=current_line[4]<58?current_line[4]-48:current_line[4]-87;
   voltage*=16;
   voltage+=current_line[5]<58?current_line[5]-48:current_line[5]-87;
   voltage*=16;
   voltage+=current_line[2]<58?current_line[2]-48:current_line[2]-87;
   voltage*=16;
   voltage+=current_line[3]<58?current_line[3]-48:current_line[3]-87;
  
   voltage=voltage/2;
   printf("Voltage: %s -> %.1f mV\n",current_line,voltage);

   sleep(1);
}

return 0;
}
