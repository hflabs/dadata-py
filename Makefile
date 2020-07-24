.DEFAULT_GOAL := help
.PHONY: changelog coverage deps help lint push test

changelog:  ## Generate changelog
	conventional-changelog -p angular -i CHANGELOG.md -s

coverage:  ## Run tests with coverage
	coverage erase
	coverage run --include=dadata/* -m pytest -ra
	coverage report -m

deps:  ## Install dependencies
	pip install black coverage flake8 httpx mypy pylint "pytest>=5.4.*,<6.*" pytest-asyncio pytest-httpx tox

lint:  ## Lint and static-check
	flake8 dadata
	pylint dadata
	mypy dadata

push:  ## Push code with tags
	git push && git push --tags

test:  ## Run tests
	pytest -ra

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done