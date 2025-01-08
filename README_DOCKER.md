```bash
sudo docker build -t quayside -f Dockerfile.dev .

# Start the container  mounted onto the current directory. Container is removed once it exits.
sudo docker run --rm -it -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd):/workspace --net=host quayside
```