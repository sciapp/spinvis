SUBDIRS := $(shell find . -mindepth 1 -maxdepth 1 -type d)

all: app

app:
	./create_dmg.sh

clean:
	@for subdir in ${SUBDIRS}; do \
		if [ -f $$subdir/Makefile ]; then \
			echo "make -C $$subdir clean"; \
			$(MAKE) -C $$subdir clean; \
		fi; \
		done
	rm -rf SpinVis.dmg

.PHONY: all app clean
