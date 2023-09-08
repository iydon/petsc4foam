import click

from .core import SuiteSparseMatrixCollection


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option('--byte-min', type=int, default=0)
@click.option('--byte-max', type=int, default=20050815)
def init(byte_min: int, byte_max: int) -> None:
    '''Initialize data directory'''
    SuiteSparseMatrixCollection \
        .fromHttp() \
        .update_data(
            overwrite=False,
            filter_kwargs={'byte_min': byte_min, 'byte_max': byte_max},
        )

@cli.command()
@click.option('--shape', type=int, default=1024)
def spy(shape) -> None:
    '''Visualize sparsity pattern of matrix'''
    SuiteSparseMatrixCollection \
        .fromHttp() \
        .spy(shape=shape, overwrite=False)


if __name__ == '__main__':
    cli()
