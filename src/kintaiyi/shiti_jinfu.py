# 《太乙統宗寶鑑》卷二十「太乙十提金賦」
# 依命宮、身宮及十二宮所臨之星匹配單星賦與合宮賦。

from __future__ import annotations

from . import config

# 單星／合星賦目（正文依煙臺圖書館藏本卷二十整理）
_ENTRIES = {
    "三基五福太乙": (
        "三基五福太乙賦",
        "君臣民福化，生成功，辰戌兮官封極品。丑未兮位至三公。延年富貴四星，"
        "臨於申亥；天資神晤，孝術幼而精通。寅卯兮終年蹇滯，巳午兮或富或窮。"
        "若值主大文昌，公卿必位；飛符同於始擊，主一世禍凶。",
        frozenset({"君基", "臣基", "民基", "五福"}),
    ),
    "飛符太乙": (
        "飛符太乙賦",
        "飛符屬火，旺於寅宮，遇午兮當臨坐廟，臨戌兮祿庫高強。亥子決波孤獨，"
        "剋妻害子，小遊忽至必敗。祖以離鄉，四神同，多生憔悴。君基合須值刑傷，"
        "當宮見於天乙，為軍為盜，相逢臨於主大，必顛必狂。",
        frozenset({"飛符"}),
    ),
    "四神太乙": (
        "四神太乙賦",
        "四神屬水，喜逢壬年。亥子兮清幽富貴，申辰兮職位高遷。四季相逢，"
        "決定離鄉棄祖。凶星轉值，須防剋刑孤單。寅午兮忠良佐主，卯巳兮家業難全。"
        "命宮臨於始擊，男淫女濫；身位逢於客大，骨月傷殘。",
        frozenset({"四神"}),
    ),
    "天乙太乙": (
        "天乙太乙賦",
        "天乙金象，孤獨凶神。丑辰兮名為將帥，申酉兮果敢功勳。飛地同宮，"
        "害子尅妻，破祖。倘臨客將，過房作贅成親。五福兮商音幸荐，巳午兮殘疾湮淪。"
        "若相逢於始擊，定然刑戮；倘得遇於主大，威振邊城。",
        frozenset({"天乙"}),
    ),
    "地乙太乙": (
        "地乙太乙賦",
        "人逢地乙，鰲寡他州。辰戌兮身榮富足，寅卯兮蹇滯淹留。主客同宮，"
        "必定為軍為旅。飛始相會，飢寒衣食難求。五福兮純誠致富，客大兮楚館秦樓。"
        "措事好華少文強作；男子得遇平生泛濫，陰人值此美態歌謳。",
        frozenset({"地乙"}),
    ),
    "小遊太乙": (
        "小遊太乙賦",
        "小遊屬木，聰敏高強。寅卯兮功業超著，申酉兮淹蹇踈狂。季術登科，"
        "亥子當為第一。身遭橫害，皆目飛始相妨。文福兮天資清爽，君臣兮祿奉朝堂。"
        "民基星居旺相，多為豪士。地乙神居絕氣，惡逆刑傷。",
        frozenset({"小游"}),
    ),
    "文計太乙": (
        "文計太乙賦",
        "文計星臨，錦繡文章。辰戌兮和平雅正，寅卯兮詭譜風狂。處世施為蓋目，"
        "相逢丑未，高門富貴；皆目同遇申辰。天地同心，為僧道君。基合必是朝郎，"
        "臣基兮才猷滿國，主客兮武鎮邊疆，越象超羣。俊傑旺宮，民福姦謀虛詐，"
        "刑憲陷位始飛。",
        frozenset({"文昌", "計神"}),
    ),
    "主客二將": (
        "主客二將賦",
        "生逢主客，武鎮邊庭。申酉兮高官貴顯，亥子兮萬里揚名。處世英雄，"
        "蓋得福君之力；臣基合會，忠良執法公卿。民基兮軍門發迹，飛始兮百事無成。"
        "蹇難貧寒夭壽；天地照破，賦性剛強勇果，文計星明。",
        frozenset({"主大", "客大"}),
    ),
    "主客二參": (
        "主客二參將賦",
        "爭奈甚而不秀，相逢始擊。常對月以栖風，五福兮權豪提挈。君基兮軍旅題名，"
        "何緣貧苦？當年目逢天地，假饒臣民救濟，可免災凶。",
        frozenset({"主參", "客參"}),
    ),
    "始擊太乙": (
        "始擊太乙賦",
        "凶神始擊，火宿炎光。寅午兮獨躔為貴，亥子兮妨害有傷。忽值君基替偽，"
        "無羈破敗，家成巨富。干臨戊癸相當，計神兮官遭囹圄，主大兮非橫則亡。"
        "宮君會於臣小，悖逆凶狼；或剋妻而損子，飛始同方。",
        frozenset({"始擊"}),
    ),
    "五福詳論": (
        "五福太乙屬土",
        "五福太乙者，上天賜福之神。在天十五年風調雨順，在地十五年玉地產靈芝，"
        "在人間十五年世出賢杰、民安國富。身命日時值此有五福：壽、富、康寧、攸好德、"
        "考終命。丑為祿庫，申為科名，辰為入廟。惟忌寅卯二宮為陷。",
        frozenset({"五福"}),
    ),
}

# 合宮賦：兩星同宮時附加（卷二十歌訣節錄）
_COMBO_HINTS = {
    frozenset({"五福", "君基"}): "五福與君基同宮：丑午辰戌乾無尅無刑，斷其富貴兩俱全。",
    frozenset({"五福", "臣基"}): "五福與臣基同宮：文必清華處台輔，武須英烈主封侯。",
    frozenset({"五福", "民基"}): "五福與民基同宮：一生富貴得雙全，遊年運限相逢著。",
    frozenset({"君基", "臣基"}): "君基臣基同會：慶會之格，貴極人臣。",
    frozenset({"文昌", "五福"}): "文昌五福與三基廟庫相逢，顯秀豐財祿。",
    frozenset({"始擊", "飛符"}): "始擊飛符同方：主一世禍凶。",
    frozenset({"始擊", "五福"}): "五福始擊相合：看旺相與否，始擊旺相五福衰亦免塵埃。",
}


def _life_core(taiyi, sex: str) -> dict:
    """命宮／身宮／十二宮排列（不觸發 taiyi_life 完整輸出）。"""
    gz = config.gangzhi(taiyi.year, taiyi.month, taiyi.day, taiyi.hour, taiyi.minute)
    yz, mz, dz = gz[0][1], gz[1][1], gz[2][1]
    di_zhi = taiyi.di_zhi
    yy = config.multi_key_dict_get(
        {tuple(di_zhi[0::2]): "陽", tuple(di_zhi[1::2]): "陰"}, yz,
    )
    direction = config.multi_key_dict_get(
        {("男陽", "女陰"): "順", ("男陰", "女陽"): "逆"}, sex + yy,
    )
    zhinum = dict(zip(di_zhi, range(1, 13)))
    twelve_gongs = "命宮,兄弟,妻妾,子孫,財帛,田宅,官祿,奴僕,疾厄,福德,相貌,父母".split(",")
    yz_arrange = dict(zip(range(1, 13), config.new_list(di_zhi, yz)))[zhinum[yz]]
    mz_arrange = dict(zip(range(1, 13), config.new_list(di_zhi, yz_arrange)))[zhinum[mz]]
    mz_arrange_r = dict(zip(range(1, 13), config.new_list(list(reversed(di_zhi)), yz_arrange)))[zhinum[mz]]
    mz1_arrange = dict(zip(range(1, 13), config.new_list(di_zhi, mz)))[zhinum[mz]]
    dz_arrange = dict(zip(range(1, 13), config.new_list(di_zhi, mz1_arrange)))[zhinum[dz]]
    dz_arrange_r = dict(zip(range(1, 13), config.new_list(list(reversed(di_zhi)), dz_arrange)))[zhinum[dz]]
    d_arrangelist = {"順": config.new_list(di_zhi, dz_arrange_r), "逆": config.new_list(di_zhi, dz_arrange)}.get(direction)
    arrangelist = {"順": config.new_list(di_zhi, mz_arrange_r), "逆": config.new_list(di_zhi, mz_arrange)}.get(direction)
    return {
        "安命宮": arrangelist[0],
        "安身宮": d_arrangelist[0],
        "十二命宮排列": dict(zip(arrangelist, twelve_gongs)),
    }


def _normalize_stars(star_list):
    if not star_list or star_list == ["空格"]:
        return set()
    out = set()
    for item in star_list:
        if not item or item == "空格":
            continue
        for name in _STAR_NAMES_ORDERED:
            if name in item:
                out.add(name)
    return out


_STAR_NAMES_ORDERED = (
    "主參", "客參", "主大", "客大", "始擊", "文昌", "計神", "小游",
    "君基", "臣基", "民基", "五福", "飛符", "四神", "天乙", "地乙",
)


def match_life(taiyi, sex: str, life: dict | None = None) -> dict:
    """依太乙命法十二宮星曜匹配十提金賦。

    life 為已算好的命法 dict 時直接取用，避免 taiyi_life → shiti_jinfu 遞迴。
    """
    palaces = taiyi.gongs_discription_list(sex)
    if life is None:
        palace_arr = taiyi._twelve_palace_map(sex)
        ming_zhi = next(iter(palace_arr))
        _core = _life_core(taiyi, sex)
        shen_zhi = _core["安身宮"]
    else:
        ming_zhi = life.get("安命宮")
        shen_zhi = life.get("安身宮")
        palace_arr = life.get("十二命宮排列", {})
    ming_stars = _normalize_stars(palaces.get("命宮", []))
    palace_by_zhi = {v: k for k, v in palace_arr.items()}
    shen_gong_name = palace_by_zhi.get(shen_zhi, "")
    shen_stars = _normalize_stars(palaces.get(shen_gong_name, []))
    all_stars = set()
    for stars in palaces.values():
        all_stars |= _normalize_stars(stars)

    focus = ming_stars | shen_stars
    entries = []
    seen = set()

    def _add(key, title, body, where, stars_hit):
        if key in seen:
            return
        seen.add(key)
        entries.append({
            "鍵": key,
            "賦名": title,
            "正文": body,
            "觸發宮": where,
            "觸發星": sorted(stars_hit),
        })

    for key, (title, body, need) in _ENTRIES.items():
        if key == "文計太乙" and need <= all_stars:
            where = []
            if need & ming_stars == need:
                where.append("命宮")
            if need & shen_stars == need and shen_gong_name:
                where.append(shen_gong_name)
            if where:
                _add(key, title, body, "、".join(where), need)
            continue
        if key == "主客二將" and {"主大", "客大"} <= all_stars:
            _add(key, title, body, "盤中", {"主大", "客大"})
            continue
        if key == "主客二參" and {"主參", "客參"} <= all_stars:
            _add(key, title, body, "盤中", {"主參", "客參"})
            continue
        for star in need:
            if star in focus:
                where = "命宮" if star in ming_stars else shen_gong_name or "身宮"
                _add(key, title, body, where, {star})
                break
            if star in all_stars and key not in seen:
                # 非命身宮亦有該星：收錄但標次要宮
                for pname, slist in palaces.items():
                    if star in _normalize_stars(slist):
                        _add(key, title, body, pname, {star})
                        break

    combos = []
    for pname, slist in palaces.items():
        ps = _normalize_stars(slist)
        if len(ps) < 2:
            continue
        for combo, hint in _COMBO_HINTS.items():
            if combo <= ps:
                combos.append({"宮": pname, "合星": sorted(combo), "歌訣": hint})

    return {
        "命宮": ming_zhi,
        "身宮": shen_zhi,
        "身宮名": shen_gong_name,
        "命宮星": sorted(ming_stars),
        "身宮星": sorted(shen_stars),
        "匹配賦": entries,
        "合宮歌訣": combos,
        "要訣": "十提金賦以命宮、身宮所臨之星為主，合宮歌訣輔之。",
    }


def format_text(result: dict) -> str:
    lines = []
    if result.get("匹配賦"):
        for e in result["匹配賦"]:
            lines.append(f"【{e['賦名']}】（{e['觸發宮']}·{'、'.join(e['觸發星'])}）")
            lines.append(e["正文"])
            lines.append("")
    if result.get("合宮歌訣"):
        lines.append("【合宮歌訣】")
        for c in result["合宮歌訣"]:
            lines.append(f"{c['宮']} {'+'.join(c['合星'])}：{c['歌訣']}")
    return "\n".join(lines).strip()