# protobuf-ci 仓库事实清单（R阶段）

> 范围：protobuf-ci 仓库 `d:\spaces\SpecWeave\external\libs\protocolbuffers\protobuf-ci`（只读）全部内容：9 个顶层 action 目录（bash/bazel/bazel-docker/ccache/checkout/composer-setup/cross-compile-protoc/docker/sccache）、internal/ 下 7 个子 action、顶层 README.md/CONTRIBUTING.md/LICENSE，以及 protobuf 主仓 .github/workflows 对本仓库的引用求证。零推测，仅记录客观存在的字段、默认值、命令与原文摘录。源码根相对路径统一省略前缀 `external/libs/protocolbuffers/protobuf-ci/`。

## 一、仓库清单与顶层文档

F-CI-001: 仓库根目录仅含：bash/、bazel/、bazel-docker/、ccache/、checkout/、composer-setup/、cross-compile-protoc/、docker/、internal/、sccache/ 十个目录，以及 CONTRIBUTING.md、LICENSE、README.md 三个文件 —— protobuf-ci/（目录清单）
F-CI-002: 顶层 README.md 原句（仓库定位）："A collection of actions and reusable workflows for CI testing in Protobuf repositories." —— README.md
F-CI-003: 顶层 README.md 原句："Actions and workflows here are expected to be reusable and changes here should apply to multiple test files/languages. If you want to make a change to a single test or language please make the change directly in the main protobuf repository." —— README.md
F-CI-004: 顶层 README.md 原句（Releases 小节）："Any change in this repository that you wish to see reflected in other Protobuf repositories requires a release."；发布流程指向内部 playbook "Making and Releasing Changes to protobuf-ci" —— README.md
F-CI-005: 顶层 CONTRIBUTING.md 要点：贡献须签署 Google CLA（https://cla.developers.google.com/）；遵循 Google's Open Source Community Guidelines；所有提交经 GitHub pull request 评审 —— CONTRIBUTING.md
F-CI-006: 顶层 LICENSE 为 Apache License Version 2.0, January 2004 —— LICENSE
F-CI-007: internal/ 目录含 7 个子 action 目录（各含一个 action.yml）：bazel-setup、ccache-setup-windows、docker-run、gcloud-auth、repository-cache-restore、repository-cache-save、setup-runner —— internal/（目录清单）

## 二、bash/action.yml（非 Bazel Bash 运行）

F-CI-008: bash/action.yml：name 为 'Non-Bazel Bash Run'，description 为 'Run a bash script for Protobuf CI testing with a non-Bazel build system' —— bash/action.yml
F-CI-009: bash/action.yml inputs：credentials（required: true，"The GCP credentials to use for reading the docker image"）、command（required: true，"A command to run in the docker image"）、bazel-version（required: false，default: "8.7.0"）、bazel-flags（required: false，"Bazel flags to use for staleness regen"） —— bash/action.yml
F-CI-010: bash/action.yml 为 composite action，步骤序列：①"Symlink current Actions repo"（`ln -fs $GH_ACTION_DIR $GH_ACTION_CLONE`，建立 `../../_actions/current` 符号链接）→ ②uses `./../../_actions/current/internal/setup-runner` → ③"Update stale files using Bazel"（uses `./../../_actions/current/bazel`，bazel-cache: regenerate-stale-files，bash: `./regenerate_stale_files.sh $BAZEL_FLAGS`）→ ④"Run"（`shell: bash, run: ${{ inputs.command }}`） —— bash/action.yml

## 三、bazel/action.yml（宿主机 Bazel 运行）

F-CI-011: bazel/action.yml：name 为 'Docker Bazel Run'，description 为 'Run a Bazel-based docker image for Protobuf CI testing' —— bazel/action.yml
F-CI-012: bazel/action.yml inputs：credentials（required: true）、bazel-cache（required: true，描述称 "This will trigger the generation of a BAZEL_CACHE environment variable inside the container"）、version（required: false，default: '6.4.0'）、bazel（required: false，"The Bazel command to run"）、bash（required: false，描述注明 "$BAZEL_FLAGS and $BAZEL_STARTUP_FLAGS will be available"）、exclude-targets（required: false，"Bazel target patterns to exclude. Each pattern must be prefixed with a minus sign."）、bazel-flags（required: false） —— bazel/action.yml
F-CI-013: bazel/action.yml 步骤：Symlink → uses internal/gcloud-auth（id: auth）→ uses internal/setup-runner → uses internal/bazel-setup（id: bazel，传入 credentials-file 与 bazel-cache） —— bazel/action.yml
F-CI-014: bazel/action.yml 平台步骤：macOS 时 `BAZEL_OSX_EXECUTE_TIMEOUT=600`（注释引用 bazelbuild/bazel#17437）；BAZELISK_PATH 按 OS 设置：Linux `~/.cache/bazelisk`、macOS `~/Library/Caches/bazelisk`、Windows `$LOCALAPPDATA\bazelisk` —— bazel/action.yml
F-CI-015: bazel/action.yml 的 Bazelisk 缓存步骤：非 PR 事件 uses `actions/cache@9255dc7a253b0ccc959486e2bca901246202afeb`（注释 # v5.0.1 (Node 24)），key `bazel-${{ runner.os }}-${{ inputs.version }}`；PR 事件改用 `actions/cache/restore`（同 SHA） —— bazel/action.yml
F-CI-016: bazel/action.yml 环境变量追加步骤：`BAZEL_FLAGS=$BAZEL_FLAGS --repository_cache=$(pwd)/${{ env.REPOSITORY_CACHE_PATH }}` 与 `BAZEL_FLAGS=$BAZEL_FLAGS ${{ inputs.bazel-flags }}`；"Validate inputs" 步骤在 bash 与 bazel 同时给出（或同时缺省）时 `exit 1`；`USE_BAZEL_VERSION=${{ inputs.version }}`；执行 `bazelisk version` —— bazel/action.yml
F-CI-017: bazel/action.yml 执行步骤：inputs.bash 存在时直接 `run: ${{ inputs.bash }}`；否则 `bazelisk ${{ steps.bazel.outputs.bazel-startup-flags }} ${{ inputs.bazel }} $BAZEL_FLAGS ... -- {exclude-targets}`；末尾非 PR 事件调用 internal/repository-cache-save —— bazel/action.yml

## 四、bazel-docker/action.yml（Docker 容器内 Bazel 运行）

F-CI-018: bazel-docker/action.yml：name 为 'Docker Bazel Run'，description 为 'Run a Bazel-based docker image for Protobuf CI testing'；inputs：credentials（required: true）、image（required: true，"The docker image to use"）、bazel-cache（required: true）、bazel（required: false）、bash（required: false，"$BAZEL_FLAGS will be available"）、exclude-targets（required: false） —— bazel-docker/action.yml
F-CI-019: bazel-docker/action.yml 步骤：Symlink → internal/gcloud-auth → internal/setup-runner → "Calculate Image Hash"（`echo ${{ inputs.image }} | md5sum | cut -f1 -d' '`）→ internal/bazel-setup（bazel-cache 追加 `-${{ steps.image-hash.outputs.value }}`，credentials-file 前缀 `/workspace/`）→ `BAZEL_FLAGS=... --repository_cache='/workspace/${{ env.REPOSITORY_CACHE_PATH }}'` → Validate inputs（同 bazel/action.yml 的 exit 1 逻辑） —— bazel-docker/action.yml
F-CI-020: bazel-docker/action.yml 执行：inputs.bash 存在时 uses internal/docker-run（run-flags: `--entrypoint "/bin/bash"`，command: `-l -c "${{ inputs.bash }}"`）；否则 uses internal/docker-run（command: `${{ inputs.bazel }} ${{ env.BAZEL_FLAGS }} ... -- {exclude-targets}`）；末尾非 PR 事件调用 internal/repository-cache-save —— bazel-docker/action.yml

## 五、ccache/action.yml（ccache 缓存配置）

F-CI-021: ccache/action.yml：name 为 'CCache Setup'，description 为 'Run a Bazel-based docker image for Protobuf CI testing'（源码原文如此）；inputs：cache-prefix（required: true，"A unique prefix to prevent cache pollution"）、support-modules（required: false，"Whether or not we need to support modules. This can result in extra cache misses."）、vsversion（default: '2019'，"The version of Visual Studio to use (Windows only)"）、ccache-version（default: '4.8'，"A pinned version of ccache"）、windows-arch（default: 'x64'） —— ccache/action.yml
F-CI-022: ccache/action.yml "Configure ccache environment variables" 步骤设置：`CCACHE_BASEDIR=${{ github.workspace }}`、`CCACHE_DIR=${{ github.workspace }}/.ccache`、`CCACHE_COMPRESS=true`、`CCACHE_COMPRESSLEVEL=5`、`CCACHE_MAXSIZE=150M`、`CCACHE_SLOPPINESS=clang_index_store,include_file_ctime,include_file_mtime,file_macro,time_macros`、`CCACHE_DIRECT=true` —— ccache/action.yml
F-CI-023: ccache/action.yml 平台安装：Windows uses internal/ccache-setup-windows（传 ccache-version/vsversion/arch）；macOS `brew install ccache`；并设置 `CCACHE_CMAKE_FLAGS=-Dprotobuf_ALLOW_CCACHE=ON -DCMAKE_C_COMPILER_LAUNCHER=$(which ccache ...) -DCMAKE_CXX_COMPILER_LAUNCHER=$(which ccache ...)` —— ccache/action.yml
F-CI-024: ccache/action.yml 缓存步骤：uses `actions/cache@9255dc7a253b0ccc959486e2bca901246202afeb # v5.0.1`；path 为 `.ccache/**` 排除 `!.ccache/lock`、`!.ccache/tmp`；key 模式 `ccache-{cache-prefix}-{github.ref_name}-{github.sha}`；restore-keys 三级：精确 SHA → 当前 ref_name → `ccache-{cache-prefix}-{github.base_ref}`（注释列出 1)同提交 2)当前分支 3)PR 基分支 的优先顺序） —— ccache/action.yml
F-CI-025: ccache/action.yml 附加步骤：support-modules 为真时追加 `CCACHE_SLOPPINESS=$CCACHE_SLOPPINESS,modules` 与 `CCACHE_DEPEND=true`；非 Linux runner 执行 `ccache -z` —— ccache/action.yml

## 六、checkout/action.yml（仓库检出）

F-CI-026: checkout/action.yml：name 为 'Github Checkout'，description 为 'Check out a Github repository'；inputs：ref（required: true，"The branch, tag or SHA to checkout"）、submodules（required: false，"Whether or not to checkout submodules"） —— checkout/action.yml
F-CI-027: checkout/action.yml 步骤：①uses `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0 (Node 24)`（参数 ref）→ ②submodules 为真时 uses `nick-fields/retry@ad984534de44a9489a53aefd81eb77f87c70dc60 # v4.0.0`（timeout_seconds: 30、retry_wait_seconds: 30、max_attempts: 5），命令为 `git submodule deinit --all -f`、`git submodule sync`、`git submodule update --force --init`（submodules=='recursive' 时追加 `--recursive`） —— checkout/action.yml

## 七、composer-setup/action.yml（PHP Composer 依赖）

F-CI-028: composer-setup/action.yml：name 为 'Composer Setup'；inputs：cache-prefix（required: true）、directory（required: false，"The directory containing composer.json"） —— composer-setup/action.yml
F-CI-029: composer-setup/action.yml 缓存：非 pull_request_target 事件 uses actions/cache@...#v5.0.1（key `composer-${{ runner.os }}-${{ inputs.cache-prefix }}-${{ hashFiles(format('{0}/composer.json', inputs.directory)) }}`，restore-keys 两级）；pull_request_target 事件改用 actions/cache/restore（注释 "will never upload a new cache (untrusted path)"）；设置 `COMPOSER_HOME=${{ github.workspace }}/composer-cache` —— composer-setup/action.yml
F-CI-030: composer-setup/action.yml 执行步骤：`composer install --ignore-platform-reqs --working-dir=${{ inputs.directory }}`（注释说明 php-actions/composer 非 Linux 不可用，引用 php-actions/composer#95）；随后 `sudo chmod -R 777 ${{ inputs.directory }}/composer.lock ${{ inputs.directory }}/vendor` —— composer-setup/action.yml

## 八、cross-compile-protoc/action.yml（交叉编译 protoc）

F-CI-031: cross-compile-protoc/action.yml：name 为 'Cross-compile protoc'，description 为 'Produces a cross-compiled protoc binary for a target architecture'；inputs：credentials（required: true）、architecture（required: true，"The target architecture to build for"）、image（required: true）；outputs：protoc（"Cross-compiled protoc location. Also output to $PROTOC"，value 来自 steps.output.outputs.protoc） —— cross-compile-protoc/action.yml
F-CI-032: cross-compile-protoc/action.yml 步骤：Symlink → uses `./../../_actions/current/bazel-docker`（bazel-cache: `xcompile-protoc/${{ inputs.architecture }}`，bash: `bazel build //:protoc_static --config=${{ inputs.architecture }} $BAZEL_FLAGS` + `cp bazel-bin/protoc_static .`）→ `echo "PROTOC=protoc-${{ inputs.architecture }}" >> $GITHUB_ENV` → `mv protoc_static $PROTOC` 并输出 —— cross-compile-protoc/action.yml

## 九、docker/action.yml（非 Bazel Docker 运行）

F-CI-033: docker/action.yml：name 为 'Docker Non-Bazel Run'，description 为 'Run a docker image for Protobuf CI testing with a non-Bazel build system'；inputs：credentials（required: true）、command（required: true）、image（required: true）、platform（required: false）、skip-staleness-check（required: false，type: boolean）、entrypoint（required: false）、extra-flags（required: false）、staleness-image（default: "us-docker.pkg.dev/protobuf-build/containers/common/linux/bazel:8.7.0-4d8e80ef93b0219fb907af9dd4596b92946995d8"） —— docker/action.yml
F-CI-034: docker/action.yml 步骤：Symlink → internal/setup-runner → 未跳过 staleness 时 uses `./../../_actions/current/bazel-docker`（image 取 inputs.staleness-image，bazel-cache: regenerate-stale-files，bash: `./regenerate_stale_files.sh $BAZEL_FLAGS`）；跳过时仅 uses internal/gcloud-auth —— docker/action.yml
F-CI-035: docker/action.yml 的 DOCKER_RUN_FLAGS 拼接：platform 给出时追加 `--platform ${{inputs.platform}}`；entrypoint 给出时追加 `--entrypoint ${{inputs.entrypoint}}`；最终 uses internal/docker-run（run-flags: `${{ env.DOCKER_RUN_FLAGS }} ${{ inputs.extra-flags }}`） —— docker/action.yml

## 十、sccache/action.yml（sccache 缓存配置）

F-CI-036: sccache/action.yml：name 为 'Setup sccache'，description 为 'Setup sccache for Protobuf CI testing'；inputs：credentials（required: true，"The GCP credentials to use for caching"）、cache-prefix（required: true）、version（required: false，default: 'v0.5.4'） —— sccache/action.yml
F-CI-037: sccache/action.yml "Validate cache name" 步骤：cache-prefix 含 '+' 或空格时 uses `actions/github-script@ed597411d8f924073f98dfc5c65a23a2325f34cd # v8.0.0 (Node 24)` 执行 `core.setFailed('Cache prefixes can't contain symbols or spaces.')` —— sccache/action.yml
F-CI-038: sccache/action.yml 环境变量步骤：internal/gcloud-auth 后设置 `SCCACHE_GCS_KEY_PATH=${{ steps.auth.outputs.credentials-file }}`、`SCCACHE_GCS_BUCKET=protobuf-sccache`、`SCCACHE_GCS_KEY_PREFIX=${{ inputs.cache-prefix }}`、`SCCACHE_IDLE_TIMEOUT=0`、`SCCACHE_IGNORE_SERVER_IO_ERROR=1`；"Enable sccache cache writing" 步骤设置 `SCCACHE_GCS_RW_MODE=READ_WRITE`（注释引用 mozilla/sccache#1886） —— sccache/action.yml
F-CI-039: sccache/action.yml 安装与预热：非 Linux uses `mozilla-actions/sccache-action@9e7fa8a12102821edf02ca5dbea1acd0f89a2696 # v0.0.10 (Node 24)`（version 参数）；随后 uses nick-fields/retry#v4.0.0（timeout_minutes: 5、retry_wait_seconds: 60、max_attempts: 5、continue_on_error: true）执行 `sccache --start-server`；并设置 `SCCACHE_CMAKE_FLAGS=-DCMAKE_C_COMPILER_LAUNCHER=sccache -DCMAKE_CXX_COMPILER_LAUNCHER=sccache`；非 Linux 执行 `sccache -z` —— sccache/action.yml

## 十一、internal/ 子 action

F-CI-040: internal/bazel-setup/action.yml：name 'Setup Bazel'；inputs：credentials-file（required: true）、bazel-cache（required: true）；outputs：bazel-flags、bazel-startup-flags；步骤设置 `BAZEL=bazelisk`、`BAZEL_FLAGS=--keep_going --test_output=errors --test_timeout=600` —— internal/bazel-setup/action.yml
F-CI-041: internal/bazel-setup/action.yml 缓存配置：bazel-cache 给出且非本地 act 运行时追加 `--google_credentials=${{ inputs.credentials-file }} --remote_cache=https://storage.googleapis.com/protobuf-bazel-cache/protobuf/gha/${{ inputs.bazel-cache }}`；非 pull_request_target 事件再追加 `--remote_upload_local_results`（注释 "External runs should never write to our caches."）；末尾调用 internal/repository-cache-restore —— internal/bazel-setup/action.yml
F-CI-042: internal/ccache-setup-windows/action.yml：name 'CCache Setup'（description 'Setup ccache for us in Windows CI'，源码原文如此）；inputs：ccache-version、vsversion、arch（均 required: true）；步骤：uses `ilammy/msvc-dev-cmd@cec98b9d092141f74527d0afa6feb2af698cfe89 # v1.12.1`；设置 `CCACHE_EXE_PATH=$LOCALAPPDATA\ccache-{version}-windows-x86_64` 并写入 GITHUB_PATH；从 https://github.com/ccache/ccache/releases/download/v{version}/ccache-{version}-windows-x86_64.zip 下载（cache key `ccache-exe-${{ inputs.ccache-version }}`） —— internal/ccache-setup-windows/action.yml
F-CI-043: internal/ccache-setup-windows/action.yml 特有变量：`CCACHE_COMPILER`（cl.exe 路径）、`CCACHE_COMPILERTYPE=msvc`；Windows 专属 `CCACHE_COMPRESSLEVEL=10`、`CCACHE_MAXSIZE=300M`（注释 "Windows caches are about 2x larger than other platforms."） —— internal/ccache-setup-windows/action.yml
F-CI-044: internal/docker-run/action.yml：name 'Run Docker'；inputs：image（required: true）、command（required: true，"A raw docker command to run"）、run-flags（required: false）、docker-cache（required: false，注释 "WARNING: loading from cache appears to be slower than pull!"） —— internal/docker-run/action.yml
F-CI-045: internal/docker-run/action.yml 安全步骤：pull_request_target 事件且 image 含 `us-docker.pkg.dev/protobuf-build/release-containers/` 时 uses actions/github-script#v8.0.0 执行 `core.setFailed('Pull requests from forks cannot use release Docker images.')`；执行 `gcloud auth configure-docker -q us-docker.pkg.dev` —— internal/docker-run/action.yml
F-CI-046: internal/docker-run/action.yml 其余步骤：uses `docker/setup-qemu-action@96fe6ef7f33517b61c61be40b68a1882f3264fb8 # v4.2.0`（continue-on-error: true，镜像 us-docker.pkg.dev/protobuf-build/containers/test/binfmt@sha256:10d6...）；docker-cache 给出时用 actions/cache（key: `${{ inputs.image }}`，path: ci/docker/）保存/加载 `docker image save --output ./ci/docker/{image}.tar`；否则 uses nick-fields/retry#v4.0.0（timeout_minutes: 5、retry_wait_seconds: 60、max_attempts: 5）执行 `docker pull -q` —— internal/docker-run/action.yml
F-CI-047: internal/docker-run/action.yml "Forward sccache arguments" 步骤：当 `SCCACHE_GCS_KEY_PATH != ''` 时生成 `-e SCCACHE_GCS_RW_MODE=... -e SCCACHE_GCS_BUCKET=... -e SCCACHE_GCS_KEY_PREFIX=... -e SCCACHE_GCS_KEY_PATH=/workspace/$(basename ...)`；最终 `docker run {args} {run-flags} -v${{ github.workspace }}:/workspace ${{ inputs.image }} ${{ inputs.command }}` —— internal/docker-run/action.yml
F-CI-048: internal/gcloud-auth/action.yml：name 'Authenticate for GCP'；inputs：credentials（required: true）；outputs：credentials-file；步骤：uses `google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093 # v3.0.0`（credentials_json 参数，仅当 env.CREDENTIALS_FILE 为空）与 `google-github-actions/setup-gcloud@26f734c2779b00b7dda794207734c511110a4368 # v3.0.0`（version: ">= 446.0.0"）；执行 `gcloud info`；输出 `CREDENTIALS_FILE` 到 GITHUB_ENV/GITHUB_OUTPUT —— internal/gcloud-auth/action.yml
F-CI-049: internal/repository-cache-restore/action.yml：name 'Restore Repository Cache'；inputs：bazel-cache（required: true）；设置 `REPOSITORY_CACHE_BASE=repository-cache-${{ github.base_ref || github.ref_name }}-${{ runner.os }}`、`REPOSITORY_CACHE_NAME=$REPOSITORY_CACHE_BASE-{bazel-cache}-{github.sha}`、`REPOSITORY_CACHE_PATH=.repository-cache`；uses actions/cache/restore（key: REPOSITORY_CACHE_NAME，restore-keys: REPOSITORY_CACHE_BASE，path: workspace 下 .repository-cache）；注释说明每个缓存 "can get up to ~500 MB and Github prunes the cache after 10 GB" —— internal/repository-cache-restore/action.yml
F-CI-050: internal/repository-cache-save/action.yml：name 'Restore Repository Cache'（description 同 restore，源码原文如此）；无 inputs；注释原句 "this action will only work if repository-cache-restore has already been called"；当 `REPOSITORY_CACHE_HASH != hashFiles(...)` 时 uses actions/cache/save（key: `REPOSITORY_CACHE_BASE-${{ github.sha }}`） —— internal/repository-cache-save/action.yml
F-CI-051: internal/setup-runner/action.yml：name 'Setup CI Runner'，无 inputs；唯一步骤 "Fix Windows line breaks"（runner.os == 'Windows' 时）：`find . -type f -print0 | xargs -0 d2u 2>/dev/null || echo "Ignoring failure"`；头部注释含 TODO(b/267357823) —— internal/setup-runner/action.yml

## 十二、protobuf 主仓对本仓库的引用（求证）

F-CI-052: protobuf 主仓 .github/workflows/ 目录共含 24 个 yaml 文件与 README.md、release_prep.sh、release_prep_test.sh；其中 14 个 yaml 引用 protocolbuffers/protobuf-ci（非任务假设的"只有 README.md"）：staleness_check.yml、test_bazel.yml、test_cpp.yml、test_csharp.yml、test_hpb.yml、test_java.yml、test_objectivec.yml、test_php_ext.yml、test_php.yml、test_python.yml、test_ruby.yml、test_rust.yml、test_upb.yml、test_yaml.yml —— protobuf 主仓 .github/workflows/（grep "protobuf-ci"）
F-CI-053: 主仓引用的全部引用形式均为 `uses: protocolbuffers/protobuf-ci/<action>@v6`，覆盖本仓库全部 9 个顶层 action：checkout@v6、bazel@v6、bazel-docker@v6、bash@v6、ccache@v6、composer-setup@v6、cross-compile-protoc@v6、docker@v6、sccache@v6 —— protobuf 主仓 .github/workflows/（grep "protobuf-ci"）
F-CI-054: 引用计数（grep 行数）：test_cpp.yml 28 处（含 3 处 bash、8 处 docker、6 处 sccache、3 处 bazel-docker、1 处 cross-compile-protoc）、test_ruby.yml 12 处、test_upb.yml 8 处、test_php.yml 8 处、test_bazel.yml 6 处、test_objectivec.yml 6 处、test_python.yml 4 处、test_java.yml 4 处（另有 2 处注释掉的引用）、test_rust.yml 4 处、test_csharp.yml 8 处、staleness_check.yml 2 处、test_hpb.yml 2 处、test_php_ext.yml 3 处、test_yaml.yml 1 处 —— protobuf 主仓 .github/workflows/（grep "protobuf-ci"）
F-CI-055: 各主仓 workflow 对 protobuf-ci 的典型组合：staleness_check.yml（checkout@v6 + bazel@v6）；test_cpp.yml（checkout + bazel-docker + cross-compile-protoc + sccache + docker + bash + bazel）；test_yaml.yml（仅 checkout@v6） —— protobuf 主仓 .github/workflows/staleness_check.yml、test_cpp.yml、test_yaml.yml
F-CI-056: 顶层 README.md Releases 小节与主仓引用相印证的事实：主仓以固定 tag `@v6` 引用，本仓库顶层 README 要求 "Any change in this repository that you wish to see reflected in other Protobuf repositories requires a release." —— README.md 与 protobuf 主仓 .github/workflows/（交叉验证）

---

**事实总条数：56 条（F-CI-001 ~ F-CI-056）**
