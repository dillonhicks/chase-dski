#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>
#include <sys/time.h>

#include "obsrv_debug.h"


#define gettimeofday(tvalue, tzone) syscall(SYS_gettimeofday, tvalue, tzone)


int
main(int argc, char **argv) {

	struct timeval tvalue;
	struct timezone tzone;
	struct timespec ts;
	
	/* Set an alarm to go off in a little while. */
	pdebug("calling gettimeofday");
	if (gettimeofday(&tvalue, &tzone)) {
		perror("gettimeofday() failed");
		exit(EXIT_FAILURE);
	}
	
	TIMEVAL_TO_TIMESPEC(&tvalue, &ts);

	pdebug("time = %d (s) %d (ns)", 
	       ((long)ts.tv_sec), ((long)ts.tv_nsec));

	pdebug("done");
	exit(EXIT_SUCCESS);
}

