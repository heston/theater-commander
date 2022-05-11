SHELL := /bin/bash

.PHONY: setup
setup:
    stat venv/bin/activate &> /dev/null || \
    virtualenv venv -p python3
    source venv/bin/activate; \
    pip install -r requirements.txt

.PHONY: install
install:
    sudo sed "s|{{DIR}}|$(dirname $(realpath theatercommander.service))|g" \
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
