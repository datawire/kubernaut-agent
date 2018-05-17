SHELL_IMAGE=python:3.6-slim

shell:
	docker run \
	-it \
	-w /app \
	-v $(PWD):/app \
	--rm $(SHELL_IMAGE) /bin/bash
