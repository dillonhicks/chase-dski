project(CANONCIAL_EXAMPLES)

if( (DEFINED DEBUG_BUILD) )
    set(CMAKE_C_FLAGS "-g -Wall -DDEBUG")
else()
    set(CMAKE_C_FLAGS "-g -Wall")	
endif()

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

set(BINARIES
  obsrv_getpid
  obsrv_write
  obsrv_sync
  obsrv_nanosleep
  obsrv_alarm
  obsrv_getcwd
  obsrv_getegid
  obsrv_geteuid
  obsrv_gettimeofday
)

foreach(BINARY ${BINARIES})  
  add_executable(${BINARY} ${BINARY}.c)
endforeach(BINARY)


