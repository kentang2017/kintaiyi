"""Grok-style sidebar for 堅太乙 — simplified two-tier layout."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Callable

import pytz
import streamlit as st

from kintaiyi.openai_compatible_client import OpenAICompatibleClient

_GREGORIAN_MIN = datetime.date(1, 1, 1)
_GREGORIAN_MAX = datetime.date(2030, 12, 31)
_BC_YEAR_MIN = -2000
_BC_YEAR_MAX = -1


def _clamp_gregorian_date(value: datetime.date) -> datetime.date:
    if value < _GREGORIAN_MIN:
        return _GREGORIAN_MIN
    if value > _GREGORIAN_MAX:
        return _GREGORIAN_MAX
    return value


def _apply_instant_hkt() -> None:
    """Set sidebar date/time to current HKT; call before date widgets render."""
    hkt_now = datetime.datetime.now(pytz.timezone("Asia/Hong_Kong"))
    st.session_state.chart_date_mode = "gregorian"
    st.session_state.chart_date = _clamp_gregorian_date(hkt_now.date())
    st.session_state.chart_year = st.session_state.chart_date.year
    st.session_state.chart_month = st.session_state.chart_date.month
    st.session_state.chart_day = st.session_state.chart_date.day
    st.session_state.chart_time = hkt_now.time().replace(second=0, microsecond=0)
    st.session_state.chart_date_input = st.session_state.chart_date
    st.session_state.chart_time_input = st.session_state.chart_time


def _init_chart_date_state(now: datetime.datetime) -> None:
    if "chart_time" not in st.session_state:
        st.session_state.chart_time = now.time().replace(second=0, microsecond=0)
    if "chart_date" not in st.session_state:
        year = int(st.session_state.get("chart_year", now.year))
        month = int(st.session_state.get("chart_month", now.month))
        day = int(st.session_state.get("chart_day", now.day))
        if _GREGORIAN_MIN.year <= year <= _GREGORIAN_MAX.year:
            try:
                st.session_state.chart_date = _clamp_gregorian_date(
                    datetime.date(year, month, day),
                )
            except ValueError:
                st.session_state.chart_date = _clamp_gregorian_date(now.date())
        else:
            st.session_state.chart_date = _clamp_gregorian_date(now.date())
    if "chart_year" not in st.session_state:
        st.session_state.chart_year = st.session_state.chart_date.year
        st.session_state.chart_month = st.session_state.chart_date.month
        st.session_state.chart_day = st.session_state.chart_date.day
    if "chart_date_mode" not in st.session_state:
        st.session_state.chart_date_mode = (
            "bc" if int(st.session_state.chart_year) < 0 else "gregorian"
        )


@dataclass
class SidebarState:
    my: int
    mm: int
    md: int
    mh: int
    mmin: int
    style: int
    tn: int
    tc: int
    sex_o: str
    rotation: str
    show_geju_markers: bool
    show_wuxing_color: bool
    show_guxu_overlay: bool
    instant: bool
    selected_model: str
    openai_api_key_input: str
    game_theory_enabled: bool


def _render_custom_provider_block(*, t: Callable[[str], str]) -> str:
    """Custom AI provider — rendered inside connection expander."""
    if "custom_provider_models" not in st.session_state:
        st.session_state.custom_provider_models = []

    st.text_input(t("custom_provider_name"), key="custom_provider_name", placeholder="自定義服務商")
    st.selectbox(
        t("custom_provider_api_mode"),
        options=[t("custom_provider_api_mode_option")],
        key="custom_provider_api_mode",
    )
    show_key = st.toggle(t("custom_provider_show_key"), key="custom_provider_show_key", value=False)
    col_key, col_check = st.columns([3, 1])
    with col_key:
        st.text_input(
            t("custom_provider_api_key"),
            type="text" if show_key else "password",
            key="custom_provider_api_key",
        )
    with col_check:
        st.markdown("<br>", unsafe_allow_html=True)
        check_key_btn = st.button(
            t("custom_provider_check_btn"), key="custom_provider_check_key_btn", width="stretch",
        )
    if check_key_btn:
        _ckey = st.session_state.get("custom_provider_api_key", "").strip()
        _chost = st.session_state.get("custom_provider_api_host", "").strip()
        _cpath = st.session_state.get("custom_provider_api_path", "").strip()
        _ccompat = st.session_state.get("custom_provider_network_compat", False)
        if not _ckey:
            st.error(t("custom_provider_api_key_missing"))
        elif not _chost:
            st.error(t("custom_provider_host_missing"))
        else:
            _proto = "http" if _ccompat else "https"
            _base_url = f"{_proto}://{_chost}{_cpath}"
            try:
                OpenAICompatibleClient(api_key=_ckey, base_url=_base_url).list_models()
                st.success(t("custom_provider_key_ok"))
            except Exception as err:
                st.error(t("custom_provider_key_fail").format(str(err)))

    col_host, col_path = st.columns(2)
    with col_host:
        st.text_input(t("custom_provider_api_host"), key="custom_provider_api_host", placeholder="api.openai.com")
    with col_path:
        st.text_input(t("custom_provider_api_path"), key="custom_provider_api_path", placeholder="/v1")
    st.toggle(t("custom_provider_network_compat"), key="custom_provider_network_compat", value=False)

    st.markdown(f"**{t('custom_provider_models_label')}**")
    col_add, col_reset, col_fetch = st.columns(3)
    with col_add:
        if st.button(t("custom_provider_add_model"), key="custom_provider_open_add_model", width="stretch"):
            st.session_state.custom_provider_add_model_open = True
    with col_reset:
        if st.button(t("custom_provider_reset_models"), key="custom_provider_reset_models_btn", width="stretch"):
            st.session_state.custom_provider_models = []
            st.rerun()
    with col_fetch:
        if st.button(t("custom_provider_fetch_models"), key="custom_provider_fetch_models_btn", width="stretch"):
            _ckey = st.session_state.get("custom_provider_api_key", "").strip()
            _chost = st.session_state.get("custom_provider_api_host", "").strip()
            _cpath = st.session_state.get("custom_provider_api_path", "").strip()
            _ccompat = st.session_state.get("custom_provider_network_compat", False)
            if not _ckey:
                st.error(t("custom_provider_api_key_missing"))
            elif not _chost:
                st.error(t("custom_provider_host_missing"))
            else:
                _proto = "http" if _ccompat else "https"
                try:
                    _fetched = OpenAICompatibleClient(
                        api_key=_ckey, base_url=f"{_proto}://{_chost}{_cpath}",
                    ).list_models()
                    st.session_state.custom_provider_models = _fetched
                    st.success(t("custom_provider_fetch_ok").format(len(_fetched)))
                    st.rerun()
                except Exception as err:
                    st.error(t("custom_provider_fetch_fail").format(str(err)))

    if st.session_state.get("custom_provider_add_model_open"):
        new_model_name = st.text_input(
            t("custom_provider_models_label"),
            key="custom_provider_new_model_input",
            placeholder=t("custom_provider_new_model_placeholder"),
            label_visibility="collapsed",
        )
        if st.button("✅", key="custom_provider_confirm_add_model") and new_model_name.strip():
            models_list = st.session_state.custom_provider_models
            if new_model_name.strip() not in models_list:
                models_list.append(new_model_name.strip())
                st.session_state.custom_provider_models = models_list
            st.session_state.custom_provider_add_model_open = False
            st.rerun()

    _custom_models = st.session_state.get("custom_provider_models", [])
    if _custom_models:
        return st.selectbox(t("ai_model"), options=_custom_models, index=0, key="custom_model_selector")
    return st.text_input(
        t("ai_model"),
        key="custom_model_direct_input",
        placeholder=t("custom_provider_new_model_placeholder"),
    )


def _render_ai_model_select(
    *,
    t: Callable[[str], str],
    ai_provider: str,
    models: dict[str, Any],
) -> str:
    """Provider-specific model picker (always visible inside AI expander)."""
    if ai_provider == "OpenAI":
        return st.selectbox(
            t("ai_model"),
            options=models["OPENAI_MODEL_OPTIONS"],
            index=0,
            key="openai_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in models["OPENAI_MODEL_DESCRIPTIONS"].items()),
        )
    if ai_provider == "xAI (Grok)":
        return st.selectbox(
            t("ai_model"),
            options=models["XAI_MODEL_OPTIONS"],
            index=0,
            key="xai_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in models["XAI_MODEL_DESCRIPTIONS"].items()),
        )
    if ai_provider == "DeepSeek":
        return st.selectbox(
            t("ai_model"),
            options=models["DEEPSEEK_MODEL_OPTIONS"],
            index=0,
            key="deepseek_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in models["DEEPSEEK_MODEL_DESCRIPTIONS"].items()),
        )
    if ai_provider == "Qwen":
        return st.selectbox(
            t("ai_model"),
            options=models["QWEN_MODEL_OPTIONS"],
            index=0,
            key="qwen_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in models["QWEN_MODEL_DESCRIPTIONS"].items()),
        )
    if ai_provider == "自定義":
        return st.session_state.get("custom_model_selector") or st.session_state.get("custom_model_direct_input") or ""
    return st.selectbox(
        t("ai_model"),
        options=models["CEREBRAS_MODEL_OPTIONS"],
        index=0,
        key="cerebras_model_selector",
        help="\n".join(f"• {k}: {v}" for k, v in models["CEREBRAS_MODEL_DESCRIPTIONS"].items()),
    )


def _render_ai_provider_block(
    *,
    t: Callable[[str], str],
    load_system_prompts: Callable[[], dict],
    save_system_prompts: Callable[[dict], bool],
    models: dict[str, Any],
) -> tuple[str, str]:
    """AI settings — provider + model on top; keys/prompts in nested expanders."""
    ai_provider = st.selectbox(
        t("ai_provider"),
        options=["Cerebras", "OpenAI", "xAI (Grok)", "DeepSeek", "Qwen", "自定義"],
        index=0,
        key="ai_provider_selector",
    )
    openai_api_key_input = ""

    with st.expander(t("sidebar_ai_connection"), expanded=False):
        if ai_provider == "OpenAI":
            openai_api_key_input = st.text_input(
                t("openai_api_key_label"),
                type="password",
                placeholder=t("openai_api_key_placeholder"),
                key="openai_api_key_input",
            )
        elif ai_provider == "xAI (Grok)":
            st.text_input(
                t("xai_api_key_label"),
                type="password",
                placeholder=t("xai_api_key_placeholder"),
                key="xai_api_key_input",
            )
        elif ai_provider == "DeepSeek":
            st.text_input(
                t("deepseek_api_key_label"),
                type="password",
                placeholder=t("deepseek_api_key_placeholder"),
                key="deepseek_api_key_input",
            )
        elif ai_provider == "Qwen":
            st.text_input(
                t("qwen_api_key_label"),
                type="password",
                placeholder=t("qwen_api_key_placeholder"),
                key="qwen_api_key_input",
            )
        elif ai_provider == "自定義":
            _render_custom_provider_block(t=t)
        else:
            st.caption(t("sidebar_ai_cerebras_hint"))

    if ai_provider == "自定義":
        selected_model = (
            st.session_state.get("custom_model_selector")
            or st.session_state.get("custom_model_direct_input")
            or ""
        )
    else:
        selected_model = _render_ai_model_select(t=t, ai_provider=ai_provider, models=models)

    system_prompts_data = load_system_prompts()
    prompts_list = system_prompts_data.get("prompts", [])
    prompt_names = [p["name"] for p in prompts_list]
    selected_prompt = system_prompts_data.get("selected")

    with st.expander(t("sidebar_ai_prompts"), expanded=False):
        if prompt_names:
            selected_index = prompt_names.index(selected_prompt) if selected_prompt in prompt_names else 0
            selected_name = st.selectbox(
                t("select_prompt"), options=prompt_names, index=selected_index,
                key="qwen_system_prompt_selector", help=t("select_prompt_help"),
            )
            system_prompts_data["selected"] = selected_name
            selected_content = next((p["content"] for p in prompts_list if p["name"] == selected_name), "")
            if "qwen_system_prompt" not in st.session_state:
                st.session_state.qwen_system_prompt = selected_content
            elif selected_name != st.session_state.get("last_selected_qwen_prompt"):
                st.session_state.qwen_system_prompt = selected_content
            st.session_state.last_selected_qwen_prompt = selected_name

            with st.expander(t("edit_prompt"), expanded=False):
                st.session_state.qwen_system_prompt = st.text_area(
                    t("edit_prompt"),
                    value=st.session_state.qwen_system_prompt,
                    height=100,
                    placeholder=t("edit_prompt_placeholder"),
                    key="qwen_system_editor",
                    label_visibility="collapsed",
                )
                col_u, col_d = st.columns(2)
                with col_u:
                    if st.button(t("update_prompt"), key="update_qwen_prompt_button"):
                        for prompt in prompts_list:
                            if prompt["name"] == selected_name:
                                prompt["content"] = st.session_state.qwen_system_prompt
                                break
                        if save_system_prompts(system_prompts_data):
                            st.toast(t("prompt_updated").format(selected_name))
                with col_d:
                    if st.button(t("delete_prompt"), key="delete_qwen_prompt_button", disabled=len(prompts_list) <= 1):
                        prompts_list = [p for p in prompts_list if p["name"] != selected_name]
                        system_prompts_data["prompts"] = prompts_list
                        if selected_name == selected_prompt and prompts_list:
                            system_prompts_data["selected"] = prompts_list[0]["name"]
                        if save_system_prompts(system_prompts_data):
                            st.toast(t("prompt_deleted").format(selected_name))
                            st.rerun()

        if "qwen_form_key_suffix" not in st.session_state:
            st.session_state.qwen_form_key_suffix = 0
        with st.expander(t("add_prompt_expander"), expanded=False):
            name_key = f"new_qwen_prompt_name_{st.session_state.qwen_form_key_suffix}"
            content_key = f"new_qwen_prompt_content_{st.session_state.qwen_form_key_suffix}"
            new_prompt_name = st.text_input(t("new_prompt_name"), key=name_key)
            new_prompt_content = st.text_area(
                t("new_prompt_content"), height=80, placeholder=t("new_prompt_placeholder"), key=content_key,
            )
            if st.button(
                t("add_prompt_btn"), key="add_qwen_prompt_button",
                disabled=not new_prompt_name or not new_prompt_content,
            ):
                if new_prompt_name in prompt_names:
                    st.error(t("prompt_exists").format(new_prompt_name))
                else:
                    prompts_list.append({"name": new_prompt_name, "content": new_prompt_content})
                    system_prompts_data["prompts"] = prompts_list
                    if save_system_prompts(system_prompts_data):
                        st.session_state.qwen_form_key_suffix += 1
                        st.toast(t("prompt_added").format(new_prompt_name))
                        st.rerun()

    with st.expander(t("advanced_settings"), expanded=False):
        st.session_state.qwen_max_tokens = st.slider(
            t("max_tokens"), 1024, 32768,
            st.session_state.get("qwen_max_tokens", 8192),
            key="qwen_max_tokens_slider", help=t("max_tokens_help"),
        )
        st.session_state.qwen_temperature = st.slider(
            t("temperature"), 0.0, 1.5,
            st.session_state.get("qwen_temperature", 0.7),
            step=0.05, key="qwen_temperature_slider", help=t("temperature_help"),
        )

    return selected_model, openai_api_key_input


def render_grok_sidebar(
    *,
    t: Callable[[str], str],
    to: Callable[[str], str],
    load_system_prompts: Callable[[], dict],
    save_system_prompts: Callable[[dict], bool],
    models: dict[str, Any],
) -> SidebarState:
    """Simplified sidebar: core chart controls visible; rest in collapsed expanders."""
    now = datetime.datetime.now(pytz.timezone("Asia/Hong_Kong"))

    st.markdown('<div class="grok-sidebar-shell">', unsafe_allow_html=True)

    # ── 語言（緊湊，置頂）──────────────────────────────────────────────
    lang_choice = st.selectbox(
        t("lang_label"),
        ["中文", "English"],
        index=0 if st.session_state.lang == "zh" else 1,
        key="lang_select",
        label_visibility="collapsed",
    )
    new_lang = "zh" if lang_choice == "中文" else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.session_state.pop("chart_meta_key", None)

    # ── 日期時間：西曆日曆（公元1年–2030）／公元前手動輸入 ─────────────────
    _init_chart_date_state(now)
    if st.session_state.pop("apply_instant_hkt", False):
        _apply_instant_hkt()
        st.session_state.trigger_instant = True

    date_mode = st.radio(
        t("date_mode_label"),
        options=["gregorian", "bc"],
        format_func=lambda m: t("date_mode_gregorian") if m == "gregorian" else t("date_mode_bc"),
        horizontal=True,
        key="chart_date_mode",
    )

    date_col, time_col = st.columns(2)
    with date_col:
        if date_mode == "gregorian":
            st.session_state.chart_date = _clamp_gregorian_date(st.session_state.chart_date)
            picked_date = st.date_input(
                t("date_label"),
                value=st.session_state.chart_date,
                min_value=_GREGORIAN_MIN,
                max_value=_GREGORIAN_MAX,
                key="chart_date_input",
            )
            st.session_state.chart_date = picked_date
            my, mm, md = picked_date.year, picked_date.month, picked_date.day
        else:
            st.caption(t("date_bc_hint"))
            bc_year = int(st.session_state.get("chart_year", _BC_YEAR_MIN))
            if bc_year > _BC_YEAR_MAX:
                bc_year = _BC_YEAR_MIN
            y_col, m_col, d_col = st.columns([2, 1, 1])
            with y_col:
                my = int(st.number_input(
                    t("year"),
                    min_value=_BC_YEAR_MIN,
                    max_value=_BC_YEAR_MAX,
                    value=bc_year,
                    step=1,
                    key="chart_year_input",
                ))
            with m_col:
                mm = int(st.number_input(
                    t("month"),
                    min_value=1,
                    max_value=12,
                    value=int(st.session_state.chart_month),
                    step=1,
                    key="chart_month_input",
                ))
            with d_col:
                md = int(st.number_input(
                    t("day"),
                    min_value=1,
                    max_value=31,
                    value=int(st.session_state.chart_day),
                    step=1,
                    key="chart_day_input",
                ))
    with time_col:
        picked_time = st.time_input(t("time_label"), value=st.session_state.chart_time, key="chart_time_input")
    st.session_state.chart_year = my
    st.session_state.chart_month = mm
    st.session_state.chart_day = md
    st.session_state.chart_time = picked_time

    mh, mmin = picked_time.hour, picked_time.minute

    # ── 主行為：立即排盤 ───────────────────────────────────────────────
    st.markdown('<div class="grok-run-chart">', unsafe_allow_html=True)
    run_chart = st.button(t("run_chart_btn"), type="primary", width="stretch", key="run_chart_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="grok-sidebar-instant">', unsafe_allow_html=True)
    if st.button(t("instant_btn"), key="instant_hkt_btn", width="stretch"):
        st.session_state.apply_instant_hkt = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    instant = bool(st.session_state.pop("trigger_instant", False)) or run_chart

    # ── 計式（預設收合）────────────────────────────────────────────────
    sex_o = "男"
    with st.expander(t("sidebar_block_method"), expanded=False):
        option = st.selectbox(
            t("chart_method"),
            ("時計太乙", "年計太乙", "月計太乙", "日計太乙", "分計太乙", "太乙命法", "太乙命法 (魔改)"),
            format_func=to,
            help=t("chart_method_hint"),
            key="chart_method_select",
        )
        acc_col, ten_col = st.columns(2)
        with acc_col:
            acum = st.selectbox(
                t("acc_years"), ("太乙統宗", "太乙金鏡", "太乙淘金歌", "太乙局"),
                format_func=to, help=t("acc_years_hint"), key="acc_years_select",
            )
        with ten_col:
            ten_ching = st.selectbox(
                t("ten_essences"), ("無", "有"), format_func=to, key="ten_essences_select",
            )
        if option in ("太乙命法", "太乙命法 (魔改)"):
            sex_o = st.selectbox(t("life_gender"), ("男", "女"), format_func=to, key="life_gender_select")

    num_dict = {
        "時計太乙": 3, "年計太乙": 0, "月計太乙": 1, "日計太乙": 2, "分計太乙": 4,
        "太乙命法": 6, "太乙命法 (魔改)": 5,
    }
    _method = st.session_state.get("chart_method_select", "時計太乙")
    _acum = st.session_state.get("acc_years_select", "太乙統宗")
    _ten = st.session_state.get("ten_essences_select", "無")
    style = num_dict[_method]
    tn = {"太乙統宗": 0, "太乙金鏡": 1, "太乙淘金歌": 2, "太乙局": 3}[_acum]
    tc = {"有": 1, "無": 0}[_ten]
    if _method in ("太乙命法", "太乙命法 (魔改)"):
        sex_o = st.session_state.get("life_gender_select", "男")

    # ── 盤面視覺（預設收合）────────────────────────────────────────────
    with st.expander(t("sidebar_block_visual"), expanded=False):
        rotation = st.selectbox(
            t("rotation_label"), ("固定", "轉動"), format_func=to, key="rotation_select",
        )
        show_geju_markers = st.toggle(t("geju_markers_toggle"), value=True, key="show_geju_markers")
        show_wuxing_color = st.toggle(t("wuxing_color_toggle"), value=True, key="show_wuxing_color")
        if _method not in ("太乙命法", "太乙命法 (魔改)"):
            st.toggle(t("guxu_overlay_toggle"), value=True, key="show_guxu_overlay")

    selected_model = models["CEREBRAS_MODEL_OPTIONS"][0]
    openai_api_key_input = ""

    # ── AI 解盤（預設收合）──────────────────────────────────────────────
    with st.expander(t("sidebar_block_ai"), expanded=False):
        selected_model, openai_api_key_input = _render_ai_provider_block(
            t=t, load_system_prompts=load_system_prompts, save_system_prompts=save_system_prompts, models=models,
        )

    # ── 進階（預設收合）────────────────────────────────────────────────
    game_theory_enabled = st.session_state.get("game_theory_toggle_switch", False)
    with st.expander(t("sidebar_block_advanced"), expanded=False):
        game_theory_enabled = st.toggle(t("game_theory_toggle"), key="game_theory_toggle_switch", value=False)
        with st.expander(t("tongyun_query_header"), expanded=False):
            tongyun_sync = st.checkbox(t("tongyun_sync_chart"), value=True, key="tongyun_sync_chart")
            if tongyun_sync:
                st.caption(t("tongyun_sync_hint").format(year=my))
            else:
                st.slider(
                    t("tongyun_query_year"), min_value=-476, max_value=2100,
                    value=int(st.session_state.get("tongyun_query_year", my)), key="tongyun_query_year",
                )
        with st.expander(t("debug_mode"), expanded=False):
            if st.toggle(t("debug_mode"), key="debug_mode_toggle", help=t("debug_help")):
                st.caption(t("debug_info"))
                st.json(st.session_state)

    st.markdown("</div>", unsafe_allow_html=True)

    rotation = st.session_state.get("rotation_select", "固定")
    show_geju_markers = st.session_state.get("show_geju_markers", True)
    show_wuxing_color = st.session_state.get("show_wuxing_color", True)
    show_guxu_overlay = st.session_state.get("show_guxu_overlay", True)
    if _method in ("太乙命法", "太乙命法 (魔改)"):
        show_guxu_overlay = False

    return SidebarState(
        my=my, mm=mm, md=md, mh=mh, mmin=mmin,
        style=style, tn=tn, tc=tc, sex_o=sex_o,
        rotation=rotation,
        show_geju_markers=show_geju_markers,
        show_wuxing_color=show_wuxing_color,
        show_guxu_overlay=show_guxu_overlay,
        instant=instant,
        selected_model=selected_model,
        openai_api_key_input=openai_api_key_input,
        game_theory_enabled=game_theory_enabled,
    )