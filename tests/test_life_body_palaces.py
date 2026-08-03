"""太乙命法「時計命法」單元測試（《太乙神數命法元集》驗算例）。"""

import pytest

from kintaiyi.kintaiyi import life_body_palaces, minute_to_virtual_branch


def test_yang_nan():
    """陽男：甲子年 + 正月寅 + 戊辰日 + 申時 → 命宮午，身宮寅。"""
    ming, shen, mp = life_body_palaces("子", "寅", "辰", "申", "男")
    assert ming == "午"
    assert shen == "寅"
    assert mp["午"] == "命宮"
    assert mp["寅"] == "疾厄"


def test_yin_nan():
    """陰男：乙丑年 + 正月寅 + … + 申時 → 逆數，命宮未。"""
    ming, shen, mp = life_body_palaces("丑", "寅", "辰", "申", "男")
    assert ming == "未"
    assert mp["未"] == "命宮"


def test_invalid_branch_raises():
    with pytest.raises(ValueError):
        life_body_palaces("子", "寅", "辰", "X", "男")
    with pytest.raises(ValueError):
        life_body_palaces("Y", "寅", "辰", "申", "男")


def test_invalid_sex_raises():
    with pytest.raises(ValueError):
        life_body_palaces("子", "寅", "辰", "申", "unknown")


def test_minute_to_virtual_branch():
    assert minute_to_virtual_branch("申", 0) == "申"
    assert minute_to_virtual_branch("申", 15) == "酉"
    assert minute_to_virtual_branch("申", 125) == "申"  # 12*10=120，繞完一圈回到申
