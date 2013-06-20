#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>
#include <errno.h>

#include "obsrv_debug.h"

#define getegid() syscall(SYS_getegid)

int main(int argc, char **argv){

        int my_egid = 0;

	pdebug("calling getegid");
	my_egid = getegid();
	if (!my_egid) {
		perror("calling getegid failed");	
		exit(EXIT_FAILURE);
	}

	pdebug("getegid returned: %d", my_egid);

	pdebug("done");
	exit(EXIT_SUCCESS);


}

