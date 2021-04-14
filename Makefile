.PHONY: push-container
push-container:
	docker-compose build
	# "docker-compose images" doesn't work
	docker tag $$(docker images webex-reminders_bot -q) docker.pkg.github.com/amthorn/webex-reminders/bot:latest
	docker push docker.pkg.github.com/amthorn/webex-reminders/bot:latest