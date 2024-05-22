# Execute all, especially Tests in the root dir of git repo
git_root_dir := $(shell git rev-parse --show-toplevel) 

.Phony: all test

all:
	# test -d 2024/ && rm -r 2024/ || return 0
	# bash tagebuch.sh
	# python3 transfer_files.py
	echo "No Recipe defined"	

# ─── Test ──────────
# On one line, because every line is executed in it's own subshell
# ie. every line is stateless
# -q: less verbose test output
test:
	@cd $(git_root_dir) && python3 -m pytest -rA -s -q tests/

# Verbose tests, ie. with normal output
vtest:
	@cd $(git_root_dir) && python3 -m pytest -rA -s tests/


