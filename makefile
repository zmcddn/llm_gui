# Define variables
DOCKER_IMAGE_NAME?= llm_gui
# DOCKER_TAG?= latest
# DOCKER_USERNAME?= your-docker-username

# Target to build the Docker image
build:
    # docker build -t $(DOCKER_USERNAME)/$(DOCKER_IMAGE_NAME):$(DOCKER_TAG) .
	docker build -t $(DOCKER_IMAGE_NAME) .

# Target to run the Docker container
run:
	docker run -it --rm \
    --security-opt seccomp=unconfined \
    -e DISPLAY=$$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $$(pwd)/conversations:/${DOCKER_IMAGE_NAME}/conversations \
    --add-host=host.docker.internal:host-gateway \
    -e OLLAMA_HOST="http://host.docker.internal:11434" \
    $(DOCKER_IMAGE_NAME)

# Target to run tests in Docker
test:
	docker run -it --rm \
    --security-opt seccomp=unconfined \
    -e DISPLAY=$$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(PWD):/llm_gui \
    $(DOCKER_IMAGE_NAME) python -m unittest test_ollama_gui.py

# Format code using uv and black
format:
	docker run -it --rm \
    -v $(PWD):/llm_gui \
    $(DOCKER_IMAGE_NAME) /bin/bash -c "\
        isort /llm_gui/*.py && \
        black /llm_gui/*.py && \
        ruff check --fix /llm_gui/*.py"

# Default target
up: build run

# Cleanup any temporary files or artifacts
.PHONY: clean
clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} \;
	find . \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f {} \;

shell:
	@container_id=$$(docker ps -qf "ancestor=$(DOCKER_IMAGE_NAME)"); \
	if [ -z "$$container_id" ]; then \
		echo "No running container found for image $(DOCKER_IMAGE_NAME)"; \
		echo "Please start the container first with 'make run'"; \
		exit 1; \
	else \
		docker exec -it $$container_id /bin/bash; \
	fi

.PHONY: build run test format up clean shell
