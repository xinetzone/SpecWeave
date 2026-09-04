# Facts: textual-demo / textual-key-recorder / .github（R 阶段·零推测）

- 采集日期：2026-09-01
- 信源根：`external/dao/action/Textualize/`（commit hash 见 `source-versions.md`）
  - textual-demo @ `babcbd1b742ba893e834fafb6f82930ae18cad65`
  - textual-key-recorder @ `8c3176ca020b261f041a4d9d7dc927a279cc69c1`
  - .github @ `37d03f2bc007387c8efa3c12bd273ea8fb1c763e`
- 规则：只写"代码里有什么"；每条标注源码相对路径；无推断词。

## 4. textual-demo（演示应用结构，F-ECO-）

- **F-ECO-01**：`external/dao/action/Textualize/textual-demo/pyproject.toml`：`[project]` name="textual-demo"，version 为 dynamic（`[tool.hatch.version]` path="src/textual_demo/__about__.py"），description="The Textual demo, packaged for your convenience"，requires-python=">=3.11"，license="MIT"；dependencies 为 `httpx>=0.27.2` 与 `textual[syntax]>=1.0.0`；build-backend 为 `hatchling.build`。
- **F-ECO-02**：`external/dao/action/Textualize/textual-demo/pyproject.toml`：`[project.scripts]` 定义 `textual-demo = "textual_demo.run:main"`；`external/dao/action/Textualize/textual-demo/src/textual_demo/__about__.py` 定义 `__version__ = "1.1.0"`。
- **F-ECO-03**：`external/dao/action/Textualize/textual-demo/src/textual_demo/run.py`：全文仅 `from textual.demo.demo_app import DemoApp`、`def main(): app = DemoApp(); app.run()` 及 `if __name__ == "__main__": main()`；仓库 `src/textual_demo/` 下除 `__init__.py`（仅 SPDX 许可头）、`__about__.py`、`run.py` 外无其他 Python 文件。
- **F-ECO-04**：`external/dao/action/Textualize/textual-demo/README.md`：首句为 "A demonstration and teaching aid for building terminals apps with Textual."；含 TIP 引用块 "No hacks were required to make your terminal do this!"；安装命令为 `uvx --python 3.12 textual-demo` 与 `pipx run --python 3.12 textual-demo`；章节含 "Game Page"（提及 Sliding Puzzle）、"Projects Page"、"Widgets Page"。
- **F-ECO-05**：`external/dao/action/Textualize/textual-demo/.python-version` 内容为 `3.12`；仓库根目录含 `uv.lock` 与 `pyproject.toml`（hatchling 构建）。

## 5. textual-key-recorder（功能，F-ECO-）

- **F-ECO-06**：`external/dao/action/Textualize/textual-key-recorder/pyproject.toml`：`[tool.poetry]` name="textual-key-recorder"，version="0.1.4"，description="A tool to help record what key names are known to Textual"，作者 "Dave Pearson <dave@textualize.io>"；依赖 `python = ">=3.8,<4.0"`、`textual = ">=0.41.0"`、`textual-fspicker = "^0.0.10"`；`[tool.poetry.scripts]` 定义 `tkrec = "textual_key_recorder.app:run"`。
- **F-ECO-07**：`external/dao/action/Textualize/textual-key-recorder/textual_key_recorder/app.py`：模块级语句 `App.BINDINGS = []`（注释 "Nuke the default Textual bindings."）；`TextualKeyRecorder(App[None])` 的 `TITLE = "Textual Key Recorder"`，`on_mount()` 执行 `self.push_screen(Main())`；`run()` 执行 `TextualKeyRecorder().run()`。
- **F-ECO-08**：`external/dao/action/Textualize/textual-key-recorder/textual_key_recorder/widgets/key_input.py`：`KeyInput(Static, can_focus=True)`，`BORDER_TITLE = "Key Press"`；定义嵌套消息 `Triggered(Message)`（字段 `key: Key`）与 `Unknown(Message)`（字段 `sequence: str`）；导入并使用 `textual._xterm_parser.XTermParser`；初始文本为 "Press a key to test..."。
- **F-ECO-09**：`external/dao/action/Textualize/textual-key-recorder/textual_key_recorder/screens/main.py`：`AdminArea(Horizontal)` 的 BINDINGS 为 `ctrl+l`（"Load progress"）、`ctrl+s`（"Save progress"）、`ctrl+q`（"Quit"）；`FILE_EXTENSION = ".tkrec"`；`FILTERS = Filters(("Textual Keys Recording", lambda p: p.suffix.lower() == AdminArea.FILE_EXTENSION))`（`Filters`/`FileOpen`/`FileSave` 导入自 `textual_fspicker`）；导入的自定义 widgets 为 Environment/ExpectedKeys/KeyInput/KeysDisplay/Notepad/TriggeredKeys/UnexpectedKeys/UnknownKeys/TestableKey。
- **F-ECO-10**：`external/dao/action/Textualize/textual-key-recorder/textual_key_recorder/widgets/keys_display.py`：`TestableKey(Option)` 定义于该文件（第 20 行），含 `from_json(cls, data: dict[str, str])` classmethod；`external/dao/action/Textualize/textual-key-recorder/textual_key_recorder/widgets/__init__.py` 的 `__all__` 列出 9 个名称（Environment/ExpectedKeys/KeyInput/KeysDisplay/Notepad/TriggeredKeys/UnexpectedKeys/UnknownKeys/TestableKey）。
- **F-ECO-11**：`external/dao/action/Textualize/textual-key-recorder/recordings/`：目录含 17 个 `.tkrec` 文件（如 `macos-iterm2-logi-keyboard.tkrec`、`debian-gnu-linux-parallels-gnome-terminal-logi-keyboard.tkrec`、`windows-parallels-terminal-logi-keyboard.tkrec`、`textual-web-mac-chrome-logi-keyboard.tkrec`），另有 `fixed-sequences.json`、`summary`、`unknown-keys` 三个非 .tkrec 文件。
- **F-ECO-12**：`external/dao/action/Textualize/textual-key-recorder/README.md` 与 `external/dao/action/Textualize/textual-key-recorder/Makefile`：README 首段为 "A tool to help record what keys result in what names in a Textual application."，安装方式为 `pipx install textual-key-recorder`，运行命令名为 `tkrec`；Makefile 的 `.DEFAULT_GOAL := run`，`package := textual_key_recorder`，`run` 目标执行 `$(python) -m $(package)`，另有 `summary`（`recordings/summary`）与 `unknown`（`recordings/unknown-keys`）目标。

## 6. .github（组织 profile README 内容，F-ECO-）

- **F-ECO-13**：`external/dao/action/Textualize/.github/` 仓库的非 .git 文件仅两个：`README.md` 与 `profile/README.md`（无 workflows、ISSUE_TEMPLATE、FUNDING.yml 等其他文件）。
- **F-ECO-14**：`external/dao/action/Textualize/.github/profile/README.md`：全文为一个指向 `https://www.textualize.io` 的 `<a>` 链接包裹 `<picture>` 元素（`<source media="(prefers-color-scheme: dark)" srcset="...">` 加 `<img src="...">`，两张图均为 github.com/Textualize/.github/assets/ 资源），后接两行文本："Move at terminal velocity." 与 "Because the [terminal is a platform](https://www.textualize.io)."。
- **F-ECO-15**：`external/dao/action/Textualize/.github/README.md`：全文仅一行 `# .github`。
