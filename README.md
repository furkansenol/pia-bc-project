# pia-bc-project
Project to simulate microservices, containerization and container orchestration for PIA Support Bootcamp project.

## How to start application
Use `make run` command to run the application. This command will build the images and run the related Kubernetes manifests.


## How to test
You can test the application by sending HTTP requests to `http://localhost:5000`.
For example you can send a POST request to `http://localhost:5000/` with body:
```json
{
    "first_name": "Furkan",
    "last_name": "Senol"
}
```
Then you can send a GET request with a query parameter like: `http://localhost:5000?user_id=66e745b7d49bb0f8ae7f41f3`