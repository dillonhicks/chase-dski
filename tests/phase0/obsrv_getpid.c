#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>
#include <errno.h>

#include "obsrv_debug.h"

#define getpid() syscall(SYS_getpid)

int main(int argc, char **argv){

        int my_pid = 0;

	pdebug("calling getpid");
	my_pid = getpid();
	if (!my_pid) {
		perror("calling getpid failed");	
		exit(EXIT_FAILURE);
	}

	pdebug("getpid returned: %d", my_pid);

	pdebug("done");
	exit(EXIT_SUCCESS);


}

