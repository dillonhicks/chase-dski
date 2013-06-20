/*
 * Adapted in part from:
 * 
 *  - http://www.gnu.org/software/libc/manual/html_node/Handler-Returns.html
 * 
 */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#define __USE_GNU
#include <sys/types.h>
#include <linux/unistd.h>
#include <sys/syscall.h>

#include "obsrv_debug.h"

#define alarm(seconds) syscall(SYS_alarm, seconds)

#define ALARM_INTERVAL 2

#define WORKLOOP_COUNT 10000

/* This flag controls termination of the main loop. */
volatile sig_atomic_t alarm_handler_called = 0;


void 
alarm_signal_handler(int sig) {
	pdebug("called signal handler");	
        alarm_handler_called = 1;
	pdebug("alarm_handler_called = 1");

}

void
workloop() {
	unsigned long i,j;
	unsigned int tmp = 0;
	
	pdebug("called workloop");
	
	for (i = 0; i < WORKLOOP_COUNT; i++)
		for (j = 0; j < WORKLOOP_COUNT; j++)
			tmp = i*j;
}


int
main(int argc, char **argv) {

	pdebug("setting alarm");
		

	/* Establish a handler for SIGALRM signals. */
	signal(SIGALRM, alarm_signal_handler);
	
	/* Set an alarm to go off in a little while. */
	if (alarm(ALARM_INTERVAL)) {
		perror("setting alarm failed");
		exit(EXIT_FAILURE);
	}
	/* Check the flag once in a while to see when to quit. */
	while (!alarm_handler_called)
		workloop();
	
	
	pdebug("done");
	exit(EXIT_SUCCESS);
}

