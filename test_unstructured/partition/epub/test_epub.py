import os
import pathlib

from unstructured.partition.epub import partition_epub
from unstructured.partition.json import partition_json
from unstructured.staging.base import elements_to_json

DIRECTORY = pathlib.Path(__file__).parent.resolve()
expected_sections = {
    "CHAPTER I THE SUN-SEEKER",
    "CHAPTER II RINKS AND SKATERS",
    "CHAPTER III TEES AND CRAMPITS",
    "CHAPTER IV TOBOGGANING",
    # not included in expected sections because TOC doesn't perfectly match with EpubHtml items
    # 'CHAPTER V ICE-HOCKEY',
    "CHAPTER VI SKI-ING",
    "CHAPTER VII NOTES ON WINTER RESORTS",
    "CHAPTER VIII FOR PARENTS AND GUARDIANS",
    "THE FULL PROJECT GUTENBERG LICENSE",
}


def test_partition_epub_from_filename():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename)
    assert len(elements) > 0
    assert elements[0].text.startswith("The Project Gutenberg eBook of Winter Sports")
    all_sections = set()
    for element in elements:
        assert element.metadata.filename == "winter-sports.epub"
        assert element.metadata.section is not None
        all_sections.add(element.metadata.section)
    assert all_sections == expected_sections


def test_partition_epub_from_filename_with_metadata_filename():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename, metadata_filename="test")
    assert len(elements) > 0
    assert all(element.metadata.filename == "test" for element in elements)
    assert all(element.metadata.section is not None for element in elements)


def test_partition_epub_from_file():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    with open(filename, "rb") as f:
        elements = partition_epub(file=f)
    assert len(elements) > 0
    assert elements[0].text.startswith("The Project Gutenberg eBook of Winter Sports")
    all_sections = set()
    for element in elements:
        assert element.metadata.filename is None
        all_sections.add(element.metadata.section)
    assert all_sections == expected_sections


def test_partition_epub_from_file_with_metadata_filename():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    with open(filename, "rb") as f:
        elements = partition_epub(file=f, metadata_filename="test")
    assert len(elements) > 0
    for element in elements:
        assert element.metadata.filename == "test"


def test_partition_epub_from_filename_exclude_metadata():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename, include_metadata=False)
    assert elements[0].metadata.filetype is None
    assert elements[0].metadata.page_name is None
    assert elements[0].metadata.filename is None
    assert elements[0].metadata.section is None


def test_partition_epub_from_file_exlcude_metadata():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    with open(filename, "rb") as f:
        elements = partition_epub(file=f, include_metadata=False)
    assert elements[0].metadata.filetype is None
    assert elements[0].metadata.page_name is None
    assert elements[0].metadata.filename is None
    assert elements[0].metadata.section is None


def test_partition_epub_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"
    mocker.patch(
        "unstructured.partition.epub.get_last_modified_date",
        return_value=mocked_last_modification_date,
    )
    elements = partition_epub(filename=filename)

    assert elements[0].metadata.last_modified == mocked_last_modification_date


def test_partition_epub_custom_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"
    expected_last_modification_date = "2020-07-05T09:24:28"

    mocker.patch(
        "unstructured.partition.html.get_last_modified_date",
        return_value=mocked_last_modification_date,
    )

    elements = partition_epub(
        filename=filename,
        metadata_last_modified=expected_last_modification_date,
    )

    assert elements[0].metadata.last_modified == expected_last_modification_date


def test_partition_epub_from_file_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"

    mocker.patch(
        "unstructured.partition.epub.get_last_modified_date_from_file",
        return_value=mocked_last_modification_date,
    )

    with open(filename, "rb") as f:
        elements = partition_epub(file=f)

    assert elements[0].metadata.last_modified == mocked_last_modification_date


def test_partition_epub_from_file_custom_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"
    expected_last_modification_date = "2020-07-05T09:24:28"

    mocker.patch(
        "unstructured.partition.html.get_last_modified_date_from_file",
        return_value=mocked_last_modification_date,
    )

    with open(filename, "rb") as f:
        elements = partition_epub(file=f, metadata_last_modified=expected_last_modification_date)

    assert elements[0].metadata.last_modified == expected_last_modification_date


def test_partition_epub_with_json():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename)
    test_elements = partition_json(text=elements_to_json(elements))

    assert len(elements) == len(test_elements)
    assert elements[0].metadata.filename == test_elements[0].metadata.filename
    assert elements[0].metadata.section == test_elements[0].metadata.section
    for i in range(len(elements)):
        elements[i] == test_elements[i]