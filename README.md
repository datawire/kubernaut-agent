# Kubernaut Agent

[![Build Status](https://travis-ci.org/datawire/kubernaut-agent.svg?branch=master)](https://travis-ci.org/datawire/kubernaut-agent)

The Kubernaut Agent is a small program that communicates with the Kubernaut Controller about cluster availability and claims.

# Installation 

## Binary

This is recommended for general purpose testing and usage. The agent is only built for Linux x86_64 as that is the only runtime platform for Kubernetes.

**TODO**

## From Source

This is only recommended if you plan to develop the agent.

```bash
git clone git@github.com:datawire/kubernaut-agent.git
cd kubernaut-agent
virtualenv venv --python python3
source venv/bin/activate
pip install -e .
```

# Development 

The agent is written and tested against Python 3.6 and built into a single binary executable using [PyInstaller](http://www.pyinstaller.org/).

## Hacking

1. Follow the [from source](#from-source) instructions to get a working source tree.

## Running Tests

In order to test and develop the agent you need a Kubernaut Controller server.

**TODO**

# Cluster Agent Protocol v1

The Kubernaut Cluster Agent Protocol v1 (CAP/1.0) is a JSON payload bi-directional WebSocket protocol with a handful of message types.

# License

Released under Apache 2.0. Please read [LICENSE](LICENSE) for details.
