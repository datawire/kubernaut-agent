import click


@click.group()
@click.option(
    "--controller-host",
    envvar="KUBERNAUT_CONTROLLER_HOST",
    help="Configure remote Kubernaut Controller host (fmt: host:port)",
    type=str
)
@click.pass_context
def cli(ctx, controller_host):
    print("Hello from the Kubernaut Agent")
