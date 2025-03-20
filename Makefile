DOCKERFILE_PATH = ./Dockerfile.test
DEFAULT_IMAGE_NAME = boton
TAG ?= latest
IMAGE_NAME = $(DEFAULT_IMAGE_NAME):$(TAG)  # Nombre completo de la imagen con tag
CONTAINER_NAME = boton

# Construir la imagen del contenedor (forzando una reconstrucción sin caché)
build:
	podman build --no-cache -t $(IMAGE_NAME) -f $(DOCKERFILE_PATH) .

# Limpiar cualquier contenedor o imagen existente
clean:
	- podman ps -aq --filter "name=$(CONTAINER_NAME)" | xargs -r podman rm -f
	- podman images --format "{{.Repository}}:{{.Tag}}" | grep "^$(DEFAULT_IMAGE_NAME)" | xargs -r podman rmi -f
	- podman images -f "dangling=true" -q | xargs -r podman rmi -f


# Ejecutar el contenedor en modo interactivo (con limpieza previa y variables de entorno)
test-local-interactivo: TAG := $(if $(filter-out $@,$(MAKECMDGOALS)),$(word 1,$(MAKECMDGOALS)),latest)
test-local-interactivo: clean build
	podman run --rm -it --name $(CONTAINER_NAME) \
		-e LLM_PROVIDER=$(LLM_PROVIDER) \
		-e LLM_ENDPOINT=$(LLM_ENDPOINT) \
		-e LLM_API_KEY=$(LLM_API_KEY) \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-e PROMPT_FILE=$(PROMPT_FILE) \
		$(IMAGE_NAME) /bin/bash

# Ejecutar el contenedor en modo automático (con limpieza previa y variables de entorno)
test-local-auto: TAG := $(if $(filter-out $@,$(MAKECMDGOALS)),$(word 1,$(MAKECMDGOALS)),latest)
test-local-auto: clean build
	podman run --rm --name $(CONTAINER_NAME) \
		-e LLM_PROVIDER=$(LLM_PROVIDER) \
		-e LLM_ENDPOINT=$(LLM_ENDPOINT) \
		-e LLM_API_KEY=$(LLM_API_KEY) \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-e PROMPT_FILE=$(PROMPT_FILE) \
		$(IMAGE_NAME) python boton/tests/main.py

# Esto evita que make interprete los params adicionales como tareas
%:
	@:
