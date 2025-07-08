default: help
all: help

help:
	@echo "Usage: make [target]"
	@echo
	@echo "Targets:"
	@echo "  build-image					Build image"
	@echo "  dev					Run server local"
	@echo "  dev-docker					Dev docker"

build-image:
	bash dockers/bump-version.sh
	bash dockers/build-image.sh

dev-docker:
	docker compose -f dockers/docker-compose.yml up --build

dev:
	bash bin/api.sh

dev-ui:
	bash bin/simple-ui.sh