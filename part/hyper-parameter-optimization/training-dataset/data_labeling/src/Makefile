BUILD = build
CMAKE = cmake
MAKE = make

.PHONY: build clean install

build:
	mkdir --parents ${BUILD}
	cd ${BUILD} && ${CMAKE} .. && ${MAKE}

clean:
	rm --recursive --force ${BUILD}

install: build
	cd ${BUILD} && ${MAKE} install
