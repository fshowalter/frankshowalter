from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Dict, List, Mapping, Optional, Set

from movie_db import _db, _imdb_s3_downloader, _imdb_s3_extractor, _table_base, humanize
from movie_db.logger import logger

FILE_NAME = 'title.basics.tsv.gz'
TABLE_NAME = 'movies'


@dataclass
class Movie(object):
    imdb_id: str
    title: str
    original_title: bool
    year: str
    runtime_minutes: str

    def __init__(self, fields: List[Optional[str]]) -> None:
        self.imdb_id = str(fields[0])
        self.title = str(fields[2])
        self.original_title = bool(fields[3])
        self.year = str(fields[5])
        self.runtime_minutes = str(fields[7])


class MoviesTable(_table_base.TableBase):
    def __init__(self) -> None:
        super().__init__(TABLE_NAME)

    def drop_and_create(self) -> None:
        ddl = """
        DROP TABLE IF EXISTS "movies";
        CREATE TABLE "movies" (
            "imdb_id" TEXT PRIMARY KEY NOT NULL,
            "title" TEXT NOT NULL,
            "year" INT NOT NULL,
            "runtime_minutes" INT);
        """

        super()._drop_and_create(ddl)

    def insert(self, movies: Mapping[str, Movie]) -> None:
        ddl = """
          INSERT INTO movies(imdb_id, title, year, runtime_minutes)
          VALUES(:imdb_id, :title, :year, :runtime_minutes);
        """
        parameter_seq = [asdict(movie) for movie in list(movies.values())]

        super()._insert(ddl=ddl, parameter_seq=parameter_seq)
        super()._add_index('title')
        super()._validate(movies)


def update() -> None:
    logger.log('==== Begin updating {}...', TABLE_NAME)

    downloaded_file_path = _imdb_s3_downloader.download(FILE_NAME, _db.DB_DIR)

    for _ in _imdb_s3_extractor.checkpoint(downloaded_file_path):
        movies = _extract_movies(downloaded_file_path)

        movies_table = MoviesTable()
        movies_table.drop_and_create()
        movies_table.insert(movies)
        title_ids.cache_clear()


@lru_cache(1)
def title_ids() -> Set[str]:
    with _db.connect() as connection:
        cursor = connection.cursor()
        cursor.row_factory = lambda cursor, row: row[0]
        return set(cursor.execute('select imdb_id from movies').fetchall())


def _extract_movies(downloaded_file_path: str) -> Mapping[str, Movie]:
    movies: Dict[str, Movie] = {}

    for fields in _imdb_s3_extractor.extract(downloaded_file_path):
        if _title_is_valid(fields):
            movies[str(fields[0])] = Movie(fields)

    logger.log('Extracted {} {}.', humanize.intcomma(len(movies)), TABLE_NAME)
    return movies


def _title_is_valid(title_line: List[Optional[str]]) -> bool:
    if title_line[1] != 'movie':
        return False
    if title_line[4] == '1':
        return False
    if title_line[5] is None:
        return False

    genres = set(str(title_line[8]).split(','))
    if 'Documentary' in genres:
        return False

    return True
