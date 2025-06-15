
DOCKER=podman
IMGTAG=registry.minikube/stelar/simple_tool:0.2.0
IMGPATH=.
DOCKERFILE=$(IMGPATH)/Dockerfile

.PHONY: all build push


all: build push

build:
	$(DOCKER) build -f $(DOCKERFILE) $(IMGPATH) -t $(IMGTAG)

push:
	$(DOCKER) push $(IMGTAG) --tls-verify=false
