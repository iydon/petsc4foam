MAKE = make


.PHONY: help openfoamcom-or-openfoamorg


help:                        ## Print the usage
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e "s/\\$$//" | sed -e "s/##//"

openfoamcom-or-openfoamorg:  ## OpenFOAM.com or OpenFOAM.org
	@cd part/$@/ && $(MAKE)
