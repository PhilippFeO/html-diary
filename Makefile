# Execute all, especially Tests in the root dir of git repo
git_root_dir := $(shell git rev-parse --show-toplevel) 
test_diary_dir := './tests/test_tagebuch'

.Phony: all test cleantest look le lt ll ode pe tf

all:
	bash tagebuch.sh

look:
	echo '' > .last_look_into_the_past.txt
	python3 look_into_the_past.py

# [t]ransfer [f]iles
tf:
	python3 transfer_files.py

# [p]ast [e]ntry
pe:
	./entry_for_past_day.sh

# [o]pen [d]iary [e]ntry
ode:
	python3 open_diary_entry.py /home/philipp/.tagebuch/2020/09-September/13-09-2020-Sonntag-Bamberg/13-09-2020-Bamberg.html


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
	@cd $(git_root_dir) && python3 -m pytest -rA -s tests/

# Verbose tests, ie. with normal output
vtest:
	@cd $(git_root_dir) && python3 -m pytest -rA -sv tests/
