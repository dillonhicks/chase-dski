
.PHONY: build clean


build:
	-rm -rf build
	mkdir build
	cd build; cmake ..; make


debug_build:
	-rm -rf build
	mkdir build
	cd build; cmake .. -DDEBUG_BUILD=1 ; make


clean:
	rm -fv *~
	rm -fr build 

# must add chase_dski/tracing to $PATH for this to work since this
# will allow easier execution of chase.py
#
test:
	cd build ;\
	(for PROG in `ls -1 ./obsrv_* `; do \
		echo $$PROG ;\
		chase.py $$PROG ;\
		strace $$PROG ;\
		echo; echo; echo; echo ;\
	done;)
