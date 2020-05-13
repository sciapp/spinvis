SUBDIRS=$(shell find . -mindepth 1 -maxdepth 1 -type d)

all: mac-app

mac-app:
	$(MAKE) -C macos app

clean:
	@for subdir in ${SUBDIRS}; do \
                if [ -f $$subdir/Makefile ]; then \
                        echo "make -C $$subdir clean"; \
                        $(MAKE) -C $$subdir clean; \
                fi; \
        done

.PHONY: all clean mac-app
