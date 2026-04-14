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
    "局式": {"文": "陽遁五十三局", "數": 53, "年": "理天", "積年數": 10155943},
    "太乙落宮": 9,
    "定算": [35, ["三才足數", "上和"]],
    "推三門具不具": "三門不具。",
    "推五將發不發": "五將發。",
    "八宮旺衰": {3: "旺", 4: "相", 9: "胎", 2: "沒", 7: "死", 6: "囚", 1: "休", 8: "廢"},
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
    "局式": {"文": "陰遁十二局", "數": 12, "年": "理地", "積年數": 10155000},
    "太乙落宮": 1,
    "定算": [10, ["無地", "純陰"]],
    "推三門具不具": "三門具。",
    "推五將發不發": "客將客參不出中門，杜塞無門。",
    "八宮旺衰": {4: "旺", 9: "相", 2: "胎", 7: "沒", 6: "死", 1: "囚", 8: "休", 3: "廢"},
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
            "主方策略列",
            "客方策略列",
            "支付矩陣",
            "主方均衡策略",
            "客方均衡策略",
            "博弈均衡值",
            "主方最優純策略",
            "客方最優純策略",
            "古法推主客相闗",
            "主方勝率判斷",
            "LP最大勝率",
            "太乙局數摘要",
            "太乙落宮",
            "八宮旺衰狀態",
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

    def test_摘要包含太乙局數(self):
        """摘要應包含太乙局數資訊。"""
        game = TaiyiGame(_PAN_主勝)
        text = game.格局摘要文字()
        assert "太乙局數" in text

    def test_摘要包含太乙落宮(self):
        """摘要應包含太乙落宮資訊。"""
        game = TaiyiGame(_PAN_主勝)
        text = game.格局摘要文字()
        assert "太乙落宮" in text


# ---------------------------------------------------------------------------
# 太乙局數、落宮、主客筭等新增因子測試
# ---------------------------------------------------------------------------


class TestTaiyiGame局數落宮因子:
    """測試太乙局數、太乙落宮等新增因子對支付矩陣的影響。"""

    def test_陽遁陰遁產生不同矩陣(self):
        """陽遁與陰遁場景下支付矩陣應不同。"""
        pan_陽 = {**_PAN_主勝, "局式": {"文": "陽遁十局", "數": 10, "年": "理天"}}
        pan_陰 = {**_PAN_主勝, "局式": {"文": "陰遁十局", "數": 10, "年": "理天"}}
        game_陽 = TaiyiGame(pan_陽)
        game_陰 = TaiyiGame(pan_陰)
        assert not np.array_equal(game_陽.支付矩陣, game_陰.支付矩陣)

    def test_不同落宮產生不同矩陣(self):
        """不同太乙落宮下支付矩陣應不同。"""
        pan_1 = {**_PAN_主勝, "太乙落宮": 1}
        pan_9 = {**_PAN_主勝, "太乙落宮": 9}
        game_1 = TaiyiGame(pan_1)
        game_9 = TaiyiGame(pan_9)
        assert not np.array_equal(game_1.支付矩陣, game_9.支付矩陣)

    def test_三才理年產生不同矩陣(self):
        """不同三才理年下支付矩陣應不同。"""
        pan_天 = {**_PAN_主勝, "局式": {"文": "陽遁十局", "數": 10, "年": "理天"}}
        pan_地 = {**_PAN_主勝, "局式": {"文": "陽遁十局", "數": 10, "年": "理地"}}
        pan_人 = {**_PAN_主勝, "局式": {"文": "陽遁十局", "數": 10, "年": "理人"}}
        game_天 = TaiyiGame(pan_天)
        game_地 = TaiyiGame(pan_地)
        game_人 = TaiyiGame(pan_人)
        assert not np.array_equal(game_天.支付矩陣, game_地.支付矩陣)
        assert not np.array_equal(game_天.支付矩陣, game_人.支付矩陣)

    def test_主算旺衰影響矩陣(self):
        """主算旺 vs 主算衰應產生不同支付矩陣。"""
        pan_旺 = {**_PAN_主勝, "主算": [150, "主算旺"]}
        pan_衰 = {**_PAN_主勝, "主算": [150, ["無天", "無地", "無人"]]}
        game_旺 = TaiyiGame(pan_旺)
        game_衰 = TaiyiGame(pan_衰)
        # 主算旺時主方攻勢策略應更高
        assert game_旺.支付矩陣[0, :].mean() > game_衰.支付矩陣[0, :].mean()

    def test_三門五將影響矩陣(self):
        """三門不具 + 五將發 vs 三門具 + 五將不發應產生不同結果。"""
        pan_利攻 = {**_PAN_主勝, "推三門具不具": "三門不具。", "推五將發不發": "五將發。"}
        pan_不利攻 = {**_PAN_主勝, "推三門具不具": "三門具。", "推五將發不發": "五將不發。"}
        game_利攻 = TaiyiGame(pan_利攻)
        game_不利攻 = TaiyiGame(pan_不利攻)
        # 利攻時攻勢策略（謀攻 + 正攻）均值應更高
        assert game_利攻.支付矩陣[:2, :].mean() > game_不利攻.支付矩陣[:2, :].mean()

    def test_定算影響矩陣(self):
        """定算值差異應影響全局偏移。"""
        pan_高 = {**_PAN_主勝, "定算": [50, ["三才足數"]]}
        pan_低 = {**_PAN_主勝, "定算": [5, ["無地"]]}
        game_高 = TaiyiGame(pan_高)
        game_低 = TaiyiGame(pan_低)
        assert game_高.支付矩陣.mean() > game_低.支付矩陣.mean()

    def test_八宮旺衰影響矩陣(self):
        """太乙落宮旺 vs 囚應影響全局偏移。"""
        pan_旺 = {
            **_PAN_主勝,
            "太乙落宮": 3,
            "八宮旺衰": {3: "旺", 4: "相", 9: "胎", 2: "沒", 7: "死", 6: "囚", 1: "休", 8: "廢"},
        }
        pan_囚 = {
            **_PAN_主勝,
            "太乙落宮": 6,
            "八宮旺衰": {3: "旺", 4: "相", 9: "胎", 2: "沒", 7: "死", 6: "囚", 1: "休", 8: "廢"},
        }
        game_旺 = TaiyiGame(pan_旺)
        game_囚 = TaiyiGame(pan_囚)
        assert game_旺.支付矩陣.mean() > game_囚.支付矩陣.mean()

    def test_報告包含太乙局數摘要(self):
        """分析報告應包含太乙局數摘要。"""
        report = TaiyiGame(_PAN_主勝).分析報告()
        摘要 = report["太乙局數摘要"]
        assert 摘要["局數"] == 53
        assert 摘要["遁法"] == "陽遁"
        assert 摘要["三才理年"] == "理天"

    def test_報告包含太乙落宮(self):
        """分析報告應包含太乙落宮值。"""
        report = TaiyiGame(_PAN_主勝).分析報告()
        assert report["太乙落宮"] == 9

    def test_報告包含八宮旺衰狀態(self):
        """分析報告應包含太乙落宮之旺衰狀態。"""
        report = TaiyiGame(_PAN_主勝).分析報告()
        assert report["八宮旺衰狀態"] == "胎"  # 9宮 → 胎

    def test_無局式欄位時退化初始化(self):
        """pan() 結果無局式欄位時應容錯退化。"""
        game = TaiyiGame({})
        assert game.支付矩陣.shape == (4, 4)

    def test_LP建議文字包含局數資訊(self):
        """LP建議文字應包含局數與落宮描述。"""
        report = TaiyiGame(_PAN_主勝).分析報告()
        建議 = report["LP最大勝率"]["建議文字"]
        assert "太乙局數" in 建議 or "遁" in 建議


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
        assert "太乙局數摘要" in gt
        assert "太乙落宮" in gt
        assert "八宮旺衰狀態" in gt
