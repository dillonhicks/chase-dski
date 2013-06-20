all:
	exit 1

CLEANPATTERNS = "*~"    \
		"*.pyc" \


CLEANPPPATTERNS = "tmp*_*_dski" 

clean:
	(for PATTERN in $(CLEANPATTERNS); do \
		find . -name $$PATTERN | xargs rm -fv ;\
	done;)


clean-pp:
	(for PATTERN in $(CLEANPPPATTERNS); do \
		find . -name $$PATTERN | xargs rm -frv ;\
	done;)


