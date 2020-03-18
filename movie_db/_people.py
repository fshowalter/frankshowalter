import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Mapping, Optional, Set

from movie_db import _db, _imdb_s3_downloader, _imdb_s3_extractor, _movies, _table_base, humanize
from movie_db.logger import logger

FILE_NAME = 'name.basics.tsv.gz'
TABLE_NAME = 'people'
NAME_REGEX = re.compile(r'^([^\s]*)\s(.*)$')


@dataclass  # noqa: WPS230
class Person(object):
    imdb_id: str
    full_name: str
    last_name: Optional[str]
    first_name: Optional[str]
    birth_year: Optional[str]
    death_year: Optional[str]
    primary_profession: Optional[str]
    known_for_title_ids: Optional[str]

    def __init__(self, fields: List[Optional[str]]) -> None:
        match = NAME_REGEX.split(str(fields[1]))
        if len(match) == 1:
            match = ['', match[0], '', '']

        self.imdb_id = str(fields[0])
        self.full_name = str(fields[1])
        self.last_name = match[2]
        self.first_name = match[1]
        self.birth_year = fields[2]
        self.death_year = fields[3]
        self.primary_profession = fields[4]
        self.known_for_title_ids = fields[5]


class PeopleTable(_table_base.TableBase):
    def __init__(self) -> None:
        super().__init__(TABLE_NAME)

    def drop_and_create(self) -> None:
        ddl = """
            DROP TABLE IF EXISTS "people";
            CREATE TABLE "people" (
                "imdb_id" TEXT PRIMARY KEY NOT NULL,
                "full_name" varchar(255) NOT NULL,
                "last_name" varchar(255),
                "first_name" varchar(255),
                "birth_year" TEXT,
                "death_year" TEXT,
                "primary_profession" TEXT,
                "known_for_title_ids" TEXT);
        """

        super()._drop_and_create(ddl)

    def insert(self, people: Mapping[str, Person]) -> None:
        ddl = """
            INSERT INTO people(
                imdb_id,
                full_name,
                last_name,
                first_name,
                birth_year,
                death_year,
                primary_profession,
                known_for_title_ids)
            VALUES(
                :imdb_id,
                :full_name,
                :last_name,
                :first_name,
                :birth_year,
                :death_year,
                :primary_profession,
                :known_for_title_ids)
        """

        parameter_seq = [asdict(person) for person in list(people.values())]

        super()._insert(ddl=ddl, parameter_seq=parameter_seq)
        super()._add_index('full_name')
        super()._validate(people)


def update() -> None:
    logger.log('==== Begin updating {}...', TABLE_NAME)

    downloaded_file_path = _imdb_s3_downloader.download(FILE_NAME, _db.DB_DIR)

    for _ in _imdb_s3_extractor.checkpoint(downloaded_file_path):
        people = _extract_people(downloaded_file_path)
        people_table = PeopleTable()
        people_table.drop_and_create()
        people_table.insert(people)


def _extract_people(downloaded_file_path: str) -> Dict[str, Person]:
    people: Dict[str, Person] = {}
    title_ids = _movies.title_ids()

    for fields in _imdb_s3_extractor.extract(downloaded_file_path):
        if _has_valid_known_for_title_ids(fields[5], title_ids):
            people[str(fields[0])] = Person(fields)

    logger.log('Extracted {} {}.', humanize.intcomma(len(people)), TABLE_NAME)
    return people


def _has_valid_known_for_title_ids(
    known_for_title_ids: Optional[str],
    valid_title_ids: Set[str],
) -> bool:
    if known_for_title_ids is None:
        return False

    for title_id in known_for_title_ids.split(','):
        if title_id in valid_title_ids:
            return True

    return False
