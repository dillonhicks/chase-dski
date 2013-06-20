#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>

#include "obsrv_debug.h"

#define write(fd, buf, count) syscall(SYS_write, fd, buf, count)

#define MESSAGE "Now, I am become Death, the destroyer of worlds.\n"
#define MESSAGE_SIZE strlen(MESSAGE)

#define STDOUT 1
#define STDERR 2


int main(int argc, char **argv){
	
	pdebug("calling write");
	
	if (!write(STDOUT, MESSAGE, MESSAGE_SIZE)) {
		perror("call to write failed\n");
		exit(EXIT_FAILURE);
	}

	pdebug("done");
	exit(EXIT_SUCCESS);
}

