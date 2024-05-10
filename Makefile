.Phony: all

all:
	test -d 2024/ && rm -r 2024/ || return 0
	bash tagebuch.sh
