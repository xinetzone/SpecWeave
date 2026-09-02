"""配置加载与默认值测试。"""

from __future__ import annotations

import os

from agent_monetize.config import Config, build_initial_loop_state, load_config

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
CONFIG_YAML = os.path.join(PROJECT_ROOT, "config.yaml")


class TestConfig:
    def test_load_default_when_missing(self) -> None:
        cfg = load_config(os.path.join(HERE, "no-such-file.yaml"))
        assert cfg.loop.rounds == 12
        assert cfg.tao.wuyou.min_certainty == 0.55
        assert cfg.tao.zhizhi.per_channel_revenue_cap == 200.0

    def test_load_yaml(self) -> None:
        cfg = load_config(CONFIG_YAML)
        assert cfg.app.name == "agent-monetize"
        assert "content_pricing" in cfg.channels
        assert cfg.channels["content_pricing"].enabled
        assert not cfg.channels["rest_report"].enabled

    def test_from_dict_ignores_unknown_keys(self) -> None:
        cfg = Config.from_dict(
            {
                "app": {"name": "x", "bogus": 1},
                "loop": {"rounds": 3, "nope": 2},
                "channels": {"a": {"enabled": False, "foo": 1}},
            }
        )
        assert cfg.app.name == "x"
        assert cfg.loop.rounds == 3
        assert cfg.channels["a"].enabled is False
        assert cfg.channels["a"].params == {"foo": 1}

    def test_build_initial_loop_state(self) -> None:
        cfg = Config.from_dict({"channels": {"on": {"enabled": True}, "off": {"enabled": False}}})
        st = build_initial_loop_state(cfg)
        assert set(st.channels) == {"on"}
        assert st.channels["on"].weight == 1.0
