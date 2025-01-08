# Docker Setup

If you have Docker Engine/Desktop isntalled, you can use the following commands to run the application locally instead of using the commands in the README.md. Just make sure that you still have your .env file in this directory (more details in the README.md).

```bash
sudo docker build -t quayside -f Dockerfile.dev .

# Start the container. Container is removed once it exits.
sudo docker run --rm -it  --net=host quayside
```