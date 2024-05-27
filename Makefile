# Execute all, especially Tests in the root dir of git repo
git_root_dir := $(shell git rev-parse --show-toplevel) 
test_diary_dir := './tests/test_tagebuch'

.Phony: all test clean cleantest look media le lt ll past

all:
	bash tagebuch.sh

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

# || return 0 necessary. Otherwise the target returns false if no test_diary_dir present.
# Then 'test' is not executed.
cleantest:
	cd $(git_root_dir) && rm -r $(test_diary_dir) || return 0

test: cleantest
	@cd $(git_root_dir) && python3 -m pytest -rA -s -q tests/

# Verbose tests, ie. with normal output
vtest:
	@cd $(git_root_dir) && python3 -m pytest -rA -s tests/


