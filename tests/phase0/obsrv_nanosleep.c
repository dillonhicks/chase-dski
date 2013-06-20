#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>

#include "obsrv_debug.h"

static struct timespec SLEEP_TIME = {
	.tv_sec = 1,
	.tv_nsec = 0
};

/* 
 * nanosleep(sleep_time, remaining_time);
 *
 * - if remaining time != null: remaining sleep time written if
 *    interrupted by a signal handler.
 */
#define nanosleep() syscall(SYS_nanosleep, &SLEEP_TIME, NULL)

int main(int argc, char **argv){
	
	pdebug("calling nanosleep");
	if(nanosleep()) {
		perror("call to nanosleep failed or interrupted\n");
		exit(EXIT_FAILURE);
	}
	
	pdebug("done");
	exit(EXIT_SUCCESS);
}

