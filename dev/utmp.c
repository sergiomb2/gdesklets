#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>

#ifdef __FreeBSD__
#include <sys/types.h>
#endif

#include <utmp.h>

int users()
{
  struct utmp buf;
  FILE *log;
  int count = 0;

  if((log = fopen("/var/run/utmp", "rb")) == NULL)
    return -1;

  while(fread(&buf, sizeof buf, 1, log) == 1)
    {
#ifdef __Linux__
      if(buf.ut_type == USER_PROCESS)
	++count;

#elif defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__)
      if(buf.ut_name[0] != '\0')
	++count;
#endif
    }

  fclose(log);

  return count;
}


void dump_info()
{
  printf("sizeof(struct utmp) -> %lu\n",
	 (unsigned long)sizeof(struct utmp));

#ifdef __Linux__
  printf("USER_PROCESS -> %d\n"
	 "offsetof(struct utmp, ut_type) -> %lu\n",
	 USER_PROCESS,
	 (unsigned long)offsetof(struct utmp, ut_type));

#elif defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__)
    printf("offsetof(struct utmp, ut_name) -> %lu\n",
	 (unsigned long)offsetof(struct utmp, ut_name));
#endif

}


int main()
{
  dump_info();

  printf("Connected users : %d\n\n", users());
  system("who -q");
  return 0;
}
