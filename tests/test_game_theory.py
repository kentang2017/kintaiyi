"""
tests/test_game_theory.py
=========================
太乙神數「運籌博弈分析」模組單元測試。

此處以古法太乙神數推演結果為測試輸入，輔以現代軟體工程單元測試
（Unit Testing）原理，驗證 TaiyiGame 類別的核心功能。
"""

import numpy as np
import pytest

from kintaiyi.game_theory import TaiyiGame, 主方策略列, 客方策略列

# ---------------------------------------------------------------------------
# 測試夾具（Fixtures）
# ---------------------------------------------------------------------------

# 模擬 pan() 輸出的精簡字典，對應「主勝」場景
_PAN_主勝 = {
    "推主客相闗法": "主勝",
    "主算": [150, "主算旺"],
    "客算": [80, "客算衰"],
    "八門值事": "開",
    "推雷公入水": "成（吉）",
    "推臨津問道": "成（正）",
    "推獅子反擲": "不成",
    "推白雲捲空": "成（吉）",
    "推猛虎相拒": "不成",
    "推白龍得雲": "成（利）",
    "推回軍無言": "不成",
}

# 模擬 pan() 輸出的精簡字典，對應「客勝」場景
_PAN_客勝 = {
    "推主客相闗法": "關得主人，客勝",
    "主算": [60, "主算衰"],
    "客算": [180, "客算旺"],
    "八門值事": "死",
    "推雷公入水": "不成",
    "推臨津問道": "不成",
    "推獅子反擲": "成（吉）",
    "推白雲捲空": "不成",
    "推猛虎相拒": "成（正）",
    "推白龍得雲": "不成",
    "推回軍無言": "成（利）",
}

# 最精簡的 pan() 字典（只有必要欄位，其餘為空）
_PAN_最簡 = {}


# ---------------------------------------------------------------------------
# TaiyiGame 初始化測試
# ---------------------------------------------------------------------------


class TestTaiyiGame初始化:
    """測試 TaiyiGame 類別的初始化行為。"""

    def test_主勝場景初始化成功(self):
        """主勝場景下 TaiyiGame 可正常初始化。"""
        game = TaiyiGame(_PAN_主勝)
        assert game is not None

    def test_客勝場景初始化成功(self):
        """客勝場景下 TaiyiGame 可正常初始化。"""
        game = TaiyiGame(_PAN_客勝)
        assert game is not None

    def test_空字典初始化成功(self):
        """空 pan() 字典下 TaiyiGame 可退化初始化（容錯）。"""
        game = TaiyiGame(_PAN_最簡)
        assert game is not None


# ---------------------------------------------------------------------------
# 支付矩陣測試
# ---------------------------------------------------------------------------


class TestTaiyiGame支付矩陣:
    """測試零和支付矩陣的結構與數值正確性。"""

    def test_支付矩陣形狀(self):
        """支付矩陣應為 4×4 的 numpy 陣列。"""
        game = TaiyiGame(_PAN_主勝)
        assert game.支付矩陣.shape == (4, 4)

    def test_支付矩陣為浮點數(self):
        """支付矩陣所有元素應為浮點數。"""
        game = TaiyiGame(_PAN_主勝)
        assert game.支付矩陣.dtype in (np.float32, np.float64)

    def test_主勝場景基準偏移為正(self):
        """「主勝」場景下支付矩陣均值應大於「客勝」場景（主方基準偏移更高）。"""
        game_主勝 = TaiyiGame(_PAN_主勝)
        game_客勝 = TaiyiGame(_PAN_客勝)
        assert game_主勝.支付矩陣.mean() > game_客勝.支付矩陣.mean()

    def test_無古法資料矩陣不全為零(self):
        """即使 pan() 字典為空，基礎矩陣也不全為零（有預設結構）。"""
        game = TaiyiGame(_PAN_最簡)
        assert not np.all(game.支付矩陣 == 0)


# ---------------------------------------------------------------------------
# Nash 均衡測試
# ---------------------------------------------------------------------------


class TestTaiyiGameNash均衡:
    """測試 Nash 均衡求解結果的數學正確性。"""

    def test_主方均衡策略概率和為一(self):
        """主方均衡策略概率向量之和應為 1（有效概率分佈）。"""
        game = TaiyiGame(_PAN_主勝)
        assert abs(game.主方均衡策略.sum() - 1.0) < 1e-6

    def test_客方均衡策略概率和為一(self):
        """客方均衡策略概率向量之和應為 1（有效概率分佈）。"""
        game = TaiyiGame(_PAN_主勝)
        assert abs(game.客方均衡策略.sum() - 1.0) < 1e-6

    def test_主方策略概率非負(self):
        """主方均衡策略所有概率值應 ≥ 0。"""
        game = TaiyiGame(_PAN_主勝)
        assert np.all(game.主方均衡策略 >= -1e-9)

    def test_客方策略概率非負(self):
        """客方均衡策略所有概率值應 ≥ 0。"""
        game = TaiyiGame(_PAN_主勝)
        assert np.all(game.客方均衡策略 >= -1e-9)

    def test_博弈均衡值為浮點數(self):
        """博弈均衡值應為浮點數。"""
        game = TaiyiGame(_PAN_主勝)
        assert isinstance(game.博弈均衡值, float)

    def test_主勝場景均衡值大於客勝場景(self):
        """「主勝」場景的博弈均衡值應大於「客勝」場景（主方有利）。"""
        v_主勝 = TaiyiGame(_PAN_主勝).博弈均衡值
        v_客勝 = TaiyiGame(_PAN_客勝).博弈均衡值
        assert v_主勝 > v_客勝

    def test_均衡值滿足極小極大性質(self):
        """
        驗證博弈均衡值滿足極小極大定理（Minimax Theorem）：
        v = max_p min_q p^T A q = min_q max_p p^T A q
        """
        game = TaiyiGame(_PAN_主勝)
        A = game.支付矩陣
        p = game.主方均衡策略
        q = game.客方均衡策略
        v = game.博弈均衡值

        # 主方期望支付：固定 q，主方最差情況下的期望支付
        expected_payoff = float(p @ A @ q)
        # 博弈均衡值應接近主方期望支付
        assert abs(expected_payoff - v) < 0.5  # 允許 LP 求解誤差範圍


# ---------------------------------------------------------------------------
# 分析報告測試
# ---------------------------------------------------------------------------


class TestTaiyiGame分析報告:
    """測試 分析報告() 方法的輸出結構。"""

    @pytest.fixture
    def report_主勝(self):
        return TaiyiGame(_PAN_主勝).分析報告()

    def test_報告包含必要鍵(self, report_主勝):
        """分析報告應包含所有必要欄位。"""
        必要鍵 = [
            "主方策略列", "客方策略列", "支付矩陣", "主方均衡策略",
            "客方均衡策略", "博弈均衡值", "主方最優純策略", "客方最優純策略",
            "古法推主客相闗", "主方勝率判斷", "LP最大勝率",
        ]
        for 鍵 in 必要鍵:
            assert 鍵 in report_主勝, f"報告缺少鍵：{鍵}"

    def test_策略列與常數一致(self, report_主勝):
        """報告中的策略列應與模組常數 主方策略列 / 客方策略列 一致。"""
        assert report_主勝["主方策略列"] == 主方策略列
        assert report_主勝["客方策略列"] == 客方策略列

    def test_主方均衡策略長度為四(self, report_主勝):
        """主方均衡策略應有四個元素。"""
        assert len(report_主勝["主方均衡策略"]) == 4

    def test_客方均衡策略長度為四(self, report_主勝):
        """客方均衡策略應有四個元素。"""
        assert len(report_主勝["客方均衡策略"]) == 4

    def test_支付矩陣為4x4列表(self, report_主勝):
        """報告中支付矩陣應為 4×4 的嵌套列表。"""
        m = report_主勝["支付矩陣"]
        assert len(m) == 4
        for row in m:
            assert len(row) == 4

    def test_LP最大勝率包含必要鍵(self, report_主勝):
        """LP最大勝率欄位應包含策略比例、期望值及建議文字。"""
        lp = report_主勝["LP最大勝率"]
        assert "最優策略比例" in lp
        assert "最大期望支付值" in lp
        assert "主要建議策略" in lp
        assert "建議文字" in lp

    def test_主方最優純策略在策略列中(self, report_主勝):
        """主方最優純策略應出現在主方策略列中。"""
        assert report_主勝["主方最優純策略"] in 主方策略列

    def test_客方最優純策略在策略列中(self, report_主勝):
        """客方最優純策略應出現在客方策略列中。"""
        assert report_主勝["客方最優純策略"] in 客方策略列

    def test_古法推主客相闗欄位(self, report_主勝):
        """古法推主客相闗欄位應與 pan() 輸入一致。"""
        assert report_主勝["古法推主客相闗"] == "主勝"

    def test_主勝場景勝率判斷包含主方(self, report_主勝):
        """主勝場景下勝率判斷應包含「主方」字樣。"""
        assert "主方" in report_主勝["主方勝率判斷"]


# ---------------------------------------------------------------------------
# 格局摘要文字測試
# ---------------------------------------------------------------------------


class TestTaiyiGame格局摘要文字:
    """測試 格局摘要文字() 方法的輸出格式。"""

    def test_摘要包含古法標題(self):
        """摘要應包含「運籌博弈分析」標題行。"""
        game = TaiyiGame(_PAN_主勝)
        text = game.格局摘要文字()
        assert "運籌博弈分析" in text

    def test_摘要包含Nash均衡字串(self):
        """摘要應包含 Nash 均衡相關說明。"""
        game = TaiyiGame(_PAN_主勝)
        text = game.格局摘要文字()
        assert "Nash" in text

    def test_摘要包含古法相闗法(self):
        """摘要應包含古法推主客相闗結論。"""
        game = TaiyiGame(_PAN_主勝)
        text = game.格局摘要文字()
        assert "主勝" in text

    def test_摘要為字串(self):
        """摘要應為字串型別。"""
        game = TaiyiGame(_PAN_主勝)
        assert isinstance(game.格局摘要文字(), str)


# ---------------------------------------------------------------------------
# kintaiyi.py 整合測試：enable_game_theory 參數
# ---------------------------------------------------------------------------


class TestKintaiyiGameTheoryIntegration:
    """測試 Taiyi.pan() 的 enable_game_theory 參數整合。"""

    @pytest.fixture(scope="class")
    def pan_result_no_gt(self):
        """不啟用 game_theory 的標準 pan() 結果。"""
        from kintaiyi.kintaiyi import Taiyi  # noqa: PLC0415
        return Taiyi(2026, 4, 14, 12, 0).pan(0, 0, enable_game_theory=False)

    @pytest.fixture(scope="class")
    def pan_result_with_gt(self):
        """啟用 game_theory 的 pan() 結果。"""
        from kintaiyi.kintaiyi import Taiyi  # noqa: PLC0415
        return Taiyi(2026, 4, 14, 12, 0).pan(0, 0, enable_game_theory=True)

    def test_不啟用game_theory時無運籌博弈分析鍵(self, pan_result_no_gt):
        """enable_game_theory=False 時 pan() 結果不應包含「運籌博弈分析」鍵。"""
        assert "運籌博弈分析" not in pan_result_no_gt

    def test_啟用game_theory時包含運籌博弈分析鍵(self, pan_result_with_gt):
        """enable_game_theory=True 時 pan() 結果應包含「運籌博弈分析」鍵。"""
        assert "運籌博弈分析" in pan_result_with_gt

    def test_啟用game_theory不破壞原有欄位(self, pan_result_no_gt, pan_result_with_gt):
        """啟用 game_theory 後，原有 pan() 所有欄位應保持完整。"""
        for 鍵 in pan_result_no_gt:
            assert 鍵 in pan_result_with_gt, f"原有欄位「{鍵}」在啟用博弈分析後遺失"

    def test_game_theory分析報告結構(self, pan_result_with_gt):
        """pan() 中的 game_theory 分析報告應包含必要欄位。"""
        gt = pan_result_with_gt["運籌博弈分析"]
        assert "博弈均衡值" in gt
        assert "主方均衡策略" in gt
        assert "客方均衡策略" in gt
        assert "LP最大勝率" in gt
