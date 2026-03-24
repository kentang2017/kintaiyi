"""Tests for kintaiyi CLI."""

import json

from typer.testing import CliRunner

from kintaiyi.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "kintaiyi" in result.output


def test_calculate_year_mode():
    result = runner.invoke(
        app, ["calculate", "--year", "1552", "--month", "9", "--day", "24", "--hour", "0", "--minute", "0", "--mode", "year"]
    )
    assert result.exit_code == 0
    assert "太乙計" in result.output


def test_calculate_date_time_shorthand():
    result = runner.invoke(
        app, ["calculate", "--date", "1552-09-24", "--time", "00:00", "--mode", "year"]
    )
    assert result.exit_code == 0
    assert "太乙計" in result.output


def test_calculate_day_mode():
    result = runner.invoke(
        app, ["calculate", "--year", "2026", "--month", "3", "--day", "24", "--hour", "12", "--minute", "30", "--mode", "day"]
    )
    assert result.exit_code == 0
    assert "日計" in result.output


def test_calculate_json_output():
    result = runner.invoke(
        app,
        ["calculate", "--year", "2026", "--month", "3", "--day", "24", "--hour", "12", "--minute", "30", "--mode", "year", "--output", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "太乙計" in data


def test_calculate_markdown_output():
    result = runner.invoke(
        app,
        ["calculate", "--year", "2026", "--month", "3", "--day", "24", "--hour", "12", "--minute", "30", "--mode", "year", "--output", "markdown"],
    )
    assert result.exit_code == 0
    assert "| 項目 | 內容 |" in result.output
    assert "| --- | --- |" in result.output


def test_calculate_life_mode():
    result = runner.invoke(
        app,
        ["calculate", "--year", "2026", "--month", "3", "--day", "24", "--hour", "12", "--minute", "30", "--mode", "life", "--sex", "male"],
    )
    assert result.exit_code == 0
    assert "性別" in result.output


def test_calculate_life_mode_requires_sex():
    result = runner.invoke(
        app,
        ["calculate", "--year", "2026", "--month", "3", "--day", "24", "--hour", "12", "--minute", "30", "--mode", "life"],
    )
    assert result.exit_code != 0


def test_calculate_invalid_date():
    result = runner.invoke(app, ["calculate", "--date", "not-a-date"])
    assert result.exit_code != 0


def test_calculate_invalid_time():
    result = runner.invoke(app, ["calculate", "--date", "2026-03-24", "--time", "bad"])
    assert result.exit_code != 0
