# Build Reference

The `kubernaut-agent` is easy and straightforward to build.

# Development Builds

There are two processes for development builds depending on the desired artifact. The first process is designed for
quick development is a standard Python source install. The second is a slightly more involved process that creates a
standalone binary.

## Prerequisites

1. Create a new Python 3.6 virtualenv at the root of the project. 

    ```shell 
    virtualenv venv --python python3`
    ```
    
2. Activate the virtualenv

    **Bash**
    ```shell
    source venv/bin/activate
    ```
    
    **Fish**
    ```shell
    source venv/bin/activate.fish
    ```

## Source "Build"

1. Run `pip install -e .`
2. Test it works by executing `kubernaut-agent --help`

## Single executable build

Single executable builds are platform dependent. In the below instructions the following variables need to be determined by the user.

| Variable  | Description |
| --------- | ----------- |
| $COMMIT   | The short git commit |
| $OS       | The operating system (`darwin` or `linux`) |
| $PLATFORM | The CPU platform (almost certainly `x86_64`) |

1. Run `./build.sh`
2. Test it works by executing `build/dist/$COMMIT/$OS/$PLATFORM/kubernaut-agent --help`

# Release Builds

Follow the [single executable build](#single-executable-build) process.
