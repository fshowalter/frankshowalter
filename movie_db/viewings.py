import os
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, List, Optional, Sequence

import yaml
from slugify import slugify

from movie_db import _table_base, humanize
from movie_db.logger import logger

TABLE_NAME = 'viewings'


@dataclass
class Viewing(object):
    imdb_id: str
    title: str
    year: int
    venue: str
    sequence: int
    date: date
    file_path: Optional[str]

    @classmethod
    def load(cls, yaml_file_path: str) -> 'Viewing':
        yaml_object = None

        with open(yaml_file_path, 'r') as yaml_file:
            yaml_object = yaml.safe_load(yaml_file)

        return cls(
            imdb_id=yaml_object['imdb_id'],
            title=yaml_object['title'],
            year=yaml_object['year'],
            venue=yaml_object['venue'],
            sequence=yaml_object['sequence'],
            date=yaml_object['date'],
            file_path=yaml_file_path,
        )

    @property
    def title_with_year(self) -> str:
        return f'{self.title} ({self.year})'

    def save(self) -> str:
        file_path = self.file_path

        if not file_path:
            slug = slugify(f'{self.sequence:04} {self.title_with_year}')
            file_path = os.path.join(TABLE_NAME, f'{slug}.yml')
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

        with open(file_path, 'wb') as output_file:
            output_file.write(self.to_yaml())

        self.file_path = file_path

        logger.log('Wrote {}', self.file_path)

        return file_path

    def to_yaml(self) -> Any:
        return yaml.dump(  # type: ignore
            {
                'sequence': self.sequence,
                'date': self.date,
                'imdb_id': self.imdb_id,
                'title': self.title_with_year,
                'venue': self.venue,
            },
            encoding='utf-8',
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )


class ViewingsTable(_table_base.TableBase):
    def __init__(self) -> None:
        super().__init__(TABLE_NAME)

    def drop_and_create(self) -> None:
        ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "movies" (
            "id"
            "movie_imdb_id" TEXT NOT NULL REFERENCES movies(id) DEFERRABLE INITIALLY DEFERRED,
            "date" DATE NOT NULL,
            "sequence" INT NOT NULL,
            "venue" TEXT NOT NULL);
        """.format(TABLE_NAME)

        super()._drop_and_create(ddl)

    def insert(self, viewings: Sequence[Viewing]) -> None:
        ddl = """
          INSERT INTO viewings(movie_imdb_id, date, sequence, venue)
          VALUES(:imdb_id, :date, :sequence, :venue);
        """
        parameter_seq = [asdict(viewing) for viewing in viewings]

        super()._insert(ddl=ddl, parameter_seq=parameter_seq)
        super()._add_index('sequence')
        super()._add_index('venue')
        super()._add_index('movie_imdb_id')
        super()._validate(viewings)


def update() -> None:
    logger.log('==== Begin updating {}...', TABLE_NAME)

    viewings = _load_viewings()
    viewings_table = ViewingsTable()
    viewings_table.drop_and_create()
    viewings_table.insert(viewings)


def _load_viewings() -> Sequence[Viewing]:
    viewings: List[Viewing] = []
    for yaml_file_path in glob(os.path.join(TABLE_NAME, '*.yml')):
        viewings.append(Viewing.load(yaml_file_path))

    logger.log('Loaded {} {}.', humanize.intcomma(len(viewings)), TABLE_NAME)
    return viewings
