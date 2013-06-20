#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>

#include "obsrv_debug.h"

#define sync() syscall(SYS_sync)

int main(int argc, char **argv){
	
	pdebug("calling sync");

	if (sync()) {
		perror("call to sync failed");
		exit(EXIT_FAILURE);
	}

	pdebug("done");
	exit(EXIT_SUCCESS);
}

