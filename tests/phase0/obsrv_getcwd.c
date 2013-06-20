#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>

#include "obsrv_debug.h"

#define getcwd(buf, count) syscall(SYS_getcwd, buf, count)

#define MAX_BUFFER_SIZE 4096

int main(int argc, char **argv) {
	
	char buffer[MAX_BUFFER_SIZE];
	
	pdebug("calling getcwd");

	if(!getcwd(&buffer, MAX_BUFFER_SIZE)) { 		
		pdebug("calling getcwd failed");
		exit(EXIT_FAILURE);
	}
	pdebug("%s", buffer);
	
	pdebug("done");

	exit(EXIT_SUCCESS);
}

