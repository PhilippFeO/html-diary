# Execute all, especially Tests in the root dir of git repo
git_root_dir := $(shell git rev-parse --show-toplevel) 

.Phony: all test clean look media le lt ll past

all: clean
	bash tagebuch.sh
	# python3 look_into_the_past.py
	# echo "No Recipe defined"	

clean:
	@# test -d ./2024/05-Mai/24-05-2024-Freitag* && rm -r ./2024/05-Mai/24-05-2024-Freitag* || return 0
	echo "Empty."

look:
	python3 look_into_the_past.py

media:
	python3 transfer_files.py

past:
	./entry_for_past_day.sh


# ─── Logs ──────────
# [l]og [e]ntry for past day
le:
	cat ./.logs/entry_for_past_day.log.txt

# [l]og [t]ransfer files
lt:
	cat ./.logs/transfer_files_add_media_files.log.txt

# [l]og [l]ook into the past
ll:
	cat ./.logs/look_into_the_past.log.txt


# ─── Test ──────────
# On one line, because every line is executed in it's own subshell
# ie. every line is stateless
# -q: less verbose test output
test:
	@cd $(git_root_dir) && python3 -m pytest -rA -s -q tests/

# Verbose tests, ie. with normal output
vtest:
	@cd $(git_root_dir) && python3 -m pytest -rA -s tests/


