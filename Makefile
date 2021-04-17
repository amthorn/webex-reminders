.PHONY: push-container
push-container:
	docker-compose build
	docker tag $$(docker-compose images -q bot) avthorn/webex-reminders:1.0
	docker push avthorn/webex-reminders:1.0