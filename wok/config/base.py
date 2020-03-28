import pathlib
import typing

import attr
import yaml


def _path_converter(path: typing.Union[str, pathlib.Path]) -> pathlib.Path:
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)
    return path.absolute().relative_to(pathlib.Path.cwd())


def _repos_converter(
    repos: typing.Iterable[typing.Union[typing.Mapping, 'Repo']]
) -> typing.Iterable['Repo']:
    return [Repo(**repo) if not isinstance(repo, Repo) else repo for repo in repos]


@attr.s(auto_attribs=True, kw_only=True)
class Repo:
    url: str
    path: pathlib.Path = attr.ib(converter=_path_converter)
    ref: str


@attr.s(auto_attribs=True, kw_only=True)
class Config:
    version: str = '1.0'
    ref: str = 'master'
    repos: typing.MutableSequence[Repo] = attr.ib(
        factory=list, converter=_repos_converter
    )
    _path: pathlib.Path = attr.ib(init=False, eq=False)

    def save(self) -> None:
        from . import schema

        print(self)
        yaml.safe_dump(
            data=schema.config.dump(obj=self),
            stream=self._path.open('w'),
            sort_keys=False,
        )

    @classmethod
    def create(cls, path: pathlib.Path) -> 'Config':
        if path.exists():
            raise FileExistsError(path.absolute())

        conf = cls()
        conf._path = path
        conf.save()

        return conf

    @classmethod
    def load(self, path: pathlib.Path) -> 'Config':
        from . import schema

        if not path.exists():
            raise FileNotFoundError(path.absolute())

        conf: Config = schema.config.load(data=yaml.safe_load(stream=path.open()))
        conf._path = path

        return conf
