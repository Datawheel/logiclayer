# LogicLayer

> A simple framework to quickly compose and use multiple functionalities as endpoints.

<a href=""><img src="https://flat.badgen.net/github/license/Datawheel/logiclayer" /></a>
<a href=""><img src="https://flat.badgen.net/github/issues/Datawheel/logiclayer" /></a>
<a href=""><img src="https://flat.badgen.net/pypi/v/logiclayer" /></a>

## Installation

This package is available in PyPI under the name `logiclayer`. You can use `pip` or `poetry` to use it in your project:

```bash
pip install logiclayer
```

## Usage

Check the directions in the [PACKAGE.md file](./PACKAGE.md).

## Development environment

To manage its dependencies, this project uses `poetry`. The [pyproject.toml](pyproject.toml) file contains all the needed dependencies an devDependencies needed. To install just run:

```bash
$ poetry install
```

### Use with VSCode + Pylance

If you intend to use Visual Studio Code to work on this project, make sure poetry creates the virtual environment within the project folder, so VSCode can find the virtual environment. To use this mode run *before* the `install` command:

```bash
$ poetry config virtualenvs.in-project true
```

## Development guidelines

Please read the [design docs](docs/DESIGN.md) before doing contributions.

## License

&copy; 2022 Datawheel, LLC.  
This project is licensed under [MIT](./LICENSE).
