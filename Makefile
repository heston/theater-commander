SHELL := /bin/bash
mkfile_dir := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: setup
setup:
	stat venv/bin/activate &> /dev/null || \
	python3 -m venv venv
	source venv/bin/activate; \
	pip install -r requirements.txt

.PHONY: install
install:
	sudo sed "s|{{DIR}}|$(mkfile_dir)|g" \
		theatercommander.service \
		> /lib/systemd/system/theatercommander.service
	sudo chmod 644 /lib/systemd/system/theatercommander.service
	sudo systemctl daemon-reload
	sudo systemctl enable theatercommander.service
	sudo systemctl start theatercommander
	sudo systemctl status theatercommander

.PHONY: uninstall
uninstall:
	sudo systemctl stop theatercommander
	sudo systemctl disable theatercommander.service
	sudo rm /lib/systemd/system/theatercommander.service
	sudo systemctl daemon-reload

.PHONY: run
run:
	source venv/bin/activate; \
	source env.sh; \
	python run.py
