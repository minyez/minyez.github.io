SRCS = $(wildcard *.yaml)
DSTS = $(patsubst %.yaml,%.md,$(SRCS))

default: $(DSTS)

%.md: %.yaml
	../tools/gallery_from_yaml.py $<
