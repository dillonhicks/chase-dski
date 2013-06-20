#ifndef OBSRV_DEBUG_H
#define OBSRV_DEBUG_H

#ifdef DEBUG
#define pdebug(fmt, args...) do {             \
  printf("[%s:%d] ", __FUNCTION__, __LINE__); \
  printf(fmt, ##args);	                      \
  printf("\n");                               \
 } while(0)

#else  /* !DEBUG */
#define pdebug(fmt, args...) do{}while(0)
#endif

#endif	/* OBSRV_DEBUG_H */
