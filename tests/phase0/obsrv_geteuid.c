#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>
#include <errno.h>

#include "obsrv_debug.h"

#define geteuid() syscall(SYS_geteuid)

int main(int argc, char **argv){

        int my_euid = 0;

	pdebug("calling getegid");
	my_euid = geteuid();
	if (!my_euid) {
		perror("calling geteuid failed");	
		exit(EXIT_FAILURE);
	}

	pdebug("geteuid returned: %d", my_euid);

	pdebug("done");
	exit(EXIT_SUCCESS);


}

