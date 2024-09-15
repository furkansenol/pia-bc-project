build:
	docker-compose build

run: build
	kubectl delete configmap env-config --ignore-not-found
	kubectl create configmap env-config --from-env-file=.env
	kubectl apply -f .\api_gateway\deployment.yaml
	kubectl apply -f .\api_gateway\service.yaml
	kubectl apply -f .\users\deployment.yaml
	kubectl apply -f .\users\service.yaml
	kubectl apply -f mongo-users-deployment.yaml
	kubectl apply -f mongo-users-service.yaml
	kubectl apply -f mongo-accounts-deployment.yaml
	kubectl apply -f mongo-accounts-service.yaml
	kubectl apply -f rabbitmq-deployment.yaml
	kubectl apply -f rabbitmq-service.yaml
	timeout 10
	kubectl apply -f .\consumer\deployment.yaml
	kubectl apply -f .\consumer\service.yaml

stop:
	kubectl delete all
