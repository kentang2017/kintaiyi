# -*- coding: utf-8 -*-
"""
Example: 太乙神數 Kintaiyi basic usage.

Usage:
    pip install kintaiyi
    python examples/basic_usage.py
"""

from kintaiyi.kintaiyi import Taiyi


def main() -> None:
    """Demonstrate basic Taiyi board calculation."""
    year, month, day, hour, minute = 1552, 9, 24, 0, 0
    ji = 0       # 0=年計; 1=月計; 2=日計; 3=時計; 4=分計
    method = 1   # 0=太乙統宗; 1=太乙金鏡; 2=太乙淘金歌; 3=太乙局

    result = Taiyi(year, month, day, hour, minute).kook(ji, method)
    print(result)


if __name__ == "__main__":
    main()
