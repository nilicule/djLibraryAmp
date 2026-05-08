"""Tests for tags module"""
from pathlib import Path
from djlibraryamp.tags import TrackInfo, parse_filename


def test_parse_filename_standard():
    assert parse_filename("Adam Beyer - Analyser - 5A - 140") == ("Adam Beyer", "Analyser")


def test_parse_filename_exactly_two_segments():
    assert parse_filename("Adam Beyer - Analyser") == ("Adam Beyer", "Analyser")


def test_parse_filename_single_segment():
    assert parse_filename("Adam Beyer") == (None, None)


def test_parse_filename_empty():
    assert parse_filename("") == (None, None)


def test_parse_filename_strips_whitespace():
    assert parse_filename("Adam Beyer  -  Analyser  - 5A") == ("Adam Beyer", "Analyser")
