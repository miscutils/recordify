VENV_DIR = .venv
VENV_RUN = source $(VENV_DIR)/bin/activate

usage:             ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

build:             ## Download dependencies
	(test `which virtualenv` || pip install virtualenv || sudo pip install virtualenv)
	@test `which sox` || (echo 'Please install the "sox" audio recording tool'; exit 1)
	@test `which mid3v2` || (echo 'Please install the "mid3v2" MP3 tag editor'; exit 1)
	@test `which lame` || (echo 'Please install the "lame" tool'; exit 1)
	@test `which wget` || (echo 'Please install the "wget" command'; exit 1)
	(test -e $(VENV_DIR) || virtualenv $(VENV_DIR))
	($(VENV_RUN) && pip install -r requirements.txt)

install:           ## Install host to Chrome "NativeMessagingHosts" folder
	bin/install_host.sh

uninstall:         ## Uninstall host from Chrome "NativeMessagingHosts" folder
	bin/uninstall_host.sh

clean:
	rm -rf $(VENV_DIR)