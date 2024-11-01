# trunk-ignore-all(trunk/ignore-does-nothing)
from __future__ import annotations

import datetime
import os
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import pytz
from pydantic import BaseModel, ValidationError

from hackathon_project_tracker.helper_logging import (
    Severity,
    log,
    log_an_exception,
    log_with_exception,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_REQUEST_TIMEOUT: int = 15
DEFAULT_TIME_ZONE: str = "US/Pacific"


class PydanticConfiguration:  # trunk-ignore(ruff/D101)
    arbitrary_types_allowed = True


def check_tokens(
    tokens: (
        dict[
            str,
            str | None,
        ]
        | None
    ),
) -> dict[str, str | None]:
    """Validates that tokens is not null."""
    if tokens is None:
        raise AttributeError

    return tokens


def create_datetime_from_timestamp_float(
    timestamp: float,
    tz: datetime.tzinfo | None = None,  # trunk-ignore(pylint/C0103)
) -> datetime.datetime:
    if tz is None:
        tz = pytz.timezone("US/Pacific")

    return datetime.datetime.fromtimestamp(
        timestamp,
        tz=tz,
    )


def create_datetime_from_timestamp_string(
    timestamp: str,
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S.%fZ",
    tz: datetime.tzinfo | None = None,  # trunk-ignore(pylint/C0103)
) -> datetime.datetime:
    if tz is None:
        tz = pytz.timezone(
            zone=DEFAULT_TIME_ZONE,
        )

    return datetime.datetime.strptime(
        timestamp,
        timestamp_format,
    ).astimezone(
        tz=pytz.timezone(
            zone=DEFAULT_TIME_ZONE,
        ),
    )


def get_input_file_paths_for_folder(
    input_folder_path: Path,
    file_extensions_to_filter: list[str] | None = None,
) -> list[str]:
    if not input_folder_path.is_dir():
        error_msg: str = f"Input Folder Path is not a directory: {input_folder_path}"
        raise ValueError(
            error_msg,
        )

    match file_extensions_to_filter:
        case None:
            log(
                the_log="File extension is null; will not filter the filepaths under the passed in directories.",
                severity=Severity.INFO,
                file=__file__,
            )

        case list():
            pass

        case _:  # trunk-ignore(pyright/reportUnnecessaryComparison)
            error_msg: str = f"File extensions needs to be a list of extensions, type passed in {type(file_extensions_to_filter)}"
            log(
                the_log=error_msg,
                severity=Severity.WARNING,
                file=__file__,
            )

    def filter_strings_that_end_with(
        string_to_match: str,
        patterns_to_match: list[str] | None,
    ) -> bool:
        if patterns_to_match is None:
            return True

        if len(patterns_to_match) == 0:
            raise AttributeError

        match_results: list[bool] = [
            string_to_match.endswith(pattern_to_match)
            for pattern_to_match in patterns_to_match
        ]
        return any(match_results)

    return sorted(
        filter(
            lambda f: (
                filter_strings_that_end_with(
                    string_to_match=f,
                    patterns_to_match=file_extensions_to_filter,
                )
            ),
            next(
                os.walk(
                    top=input_folder_path,
                ),
                (
                    None,
                    None,
                    [],
                ),
            )[2],
        ),
    )


def get_object_with_lowest_index(
    object_list: Sequence[object],
    object_list_to_validate_against: list[object],
) -> object | None:
    class ObjectWithIndex(NamedTuple):
        the_object: object
        object_index: int

    object_with_index_list: list[ObjectWithIndex] = [
        ObjectWithIndex(
            the_object=the_object,
            object_index=object_list_to_validate_against.index(
                the_object,
            ),
        )
        for the_object in object_list
        if the_object in object_list_to_validate_against
    ]
    try:
        return min(
            object_with_index_list,
            key=lambda object_with_index: object_with_index.object_index,
        ).the_object

    except ValueError:
        return None


def github_strip_url(
    repo_url: str,
) -> str:
    github_url: str = "github.com/"
    github_string_index: int = repo_url.index(
        github_url,
    )
    return repo_url[github_string_index + len(github_url) :]


def is_email_address(
    email_address_candidate: str,
) -> bool:
    return "@" in email_address_candidate


def load_file_then_dump_as_string(
    file_path: Path,
) -> str:
    with file_path.open(
        mode="r+",
        encoding="UTF-8",
    ) as file:
        return str(file.read())


def load_json_from_gcp(
    url: str | None = None,
) -> str:
    import requests

    if url is None:
        raise AttributeError

    log(
        the_log=f"URL to load from GCP: {url}",
        severity=Severity.INFO,
        file=__file__,
    )
    return str(
        requests.get(
            url=url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
        ).text,
    )


def validate_response_message_success(
    class_name: str,
    file: str,
) -> None:
    log(
        the_log=f"{file} : {class_name} : Validated successfully",
        severity=Severity.DEBUG,
        file=file,
    )


def validate_response_is_successful(
    json_data_or_obj: str | dict,
    response_type_list: list[
        tuple[
            type[BaseModel],
            bool,  # boolean is whether or not to log the exception thrown if the modeler fails to parse the response
        ]
    ],
    file: str,
) -> BaseModel:
    """validate_response_is_successful Checks the response against a list of possible Base Models.

    Throws an exception if none of the models match!

    :raises AssertionError: Need a non-empty list of Base Models to validate against
    :raises ValueError: The input payload type should be a string or a dictionary so it can be validated with a pydantic model
    :raises log_with_exception: Thrown when none of the Base Models can parse the response
    :return BaseModel: The Base Model that successfully parsed the response
    """
    log(
        the_log="Validating response is successful",
        severity=Severity.DEBUG,
        file=__file__,
    )
    log(
        the_log=f"{json_data_or_obj!s}",
        severity=Severity.DEBUG,
        file=__file__,
    )

    error_msg: str = "Response Type List: Empty"
    if len(response_type_list) == 0:
        raise AssertionError(
            error_msg,
        )

    def parse_based_on_type(
        response_type_to_parse_with: type[BaseModel],
    ) -> BaseModel:
        match json_data_or_obj:

            case str():
                return response_type_to_parse_with.model_validate_json(
                    json_data=json_data_or_obj,
                )

            case dict():
                return response_type_to_parse_with.model_validate(
                    obj=json_data_or_obj,
                )

        error_msg: str = (
            f"Input Payload: Type: Could not be matched: {type(json_data_or_obj)}"
        )
        raise ValueError(
            error_msg,
            Severity.ERROR,
        )

    response_type: type[BaseModel]
    should_log_exception: bool
    for response_item in response_type_list:
        response_type, should_log_exception = response_item
        response_parsed: BaseModel | None = None
        try:
            response_parsed = parse_based_on_type(
                response_type_to_parse_with=response_type,
            )

        except ValidationError as exception:
            if should_log_exception:
                log(
                    the_log=str(json_data_or_obj),
                    severity=Severity.DEBUG,
                    file=file,
                )
                log_an_exception(
                    exception=exception,
                    file=file,
                )
                log(
                    the_log=f"Validation failed for response type: {response_type.__name__}",
                    severity=Severity.DEBUG,
                    file=file,
                )

            continue

        try:
            response_parsed.validate_response()

        except AttributeError:
            log(
                the_log=f"Validate response does not exist for response type: {response_type.__name__}",
                severity=Severity.DEBUG,
                file=__file__,
            )

        return response_parsed

    raise log_with_exception(
        the_log=f"Response could not be parsed, none of the models match.\n{json_data_or_obj}",
        severity=Severity.ERROR,
        file=__file__,
    )


def write_to_disk(
    stream: str,
    file_path: Path,
) -> None:
    folder_path: str
    folder_path, _ = os.path.split(file_path)
    Path(folder_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    with file_path.open(
        mode="w+",
        encoding="UTF-8",
    ) as writer:
        writer.write(
            stream,
        )


class FileType(Enum):
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"

    @classmethod
    def from_filepath(
        cls: type[FileType],
        input_file_path: Path,
    ) -> FileType:
        if not input_file_path.is_file():
            raise ValueError

        tail: str
        _, tail = os.path.split(
            p=input_file_path,
        )
        extension: str
        _, extension = tail.split(".")
        return FileType(extension)

    def fetch_json(
        self: FileType,
        file_path: Path,
    ) -> dict:
        match self:

            case FileType.CSV:
                import pandas as pd

                data = pd.read_csv(
                    filepath_or_buffer=file_path,
                )
                return dict(
                    data.to_dict(
                        orient="list",
                    ),
                )

            case FileType.JSON:
                import json

                return dict(
                    json.loads(
                        s=load_file_then_dump_as_string(
                            file_path=file_path,
                        ),
                    ),
                )

            case FileType.YAML:
                import yaml

                return dict(
                    yaml.safe_load(
                        stream=load_file_then_dump_as_string(
                            file_path=file_path,
                        ),
                    ),
                )

        raise ValueError
