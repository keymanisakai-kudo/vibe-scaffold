# vibe_scaffold/cli.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单兵项目脚手架工具 v2 - pipx 版本

特点：
- 支持项目类型: web-app / service-api / tool-script
- 支持模板: default / fintech-dapp
- 自动创建目录结构 + docs 模板 + 简单 git 初始化
- 写入 project_meta.json 方便后续自动化使用
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from textwrap import dedent

PROJECT_TYPES = ["web-app", "service-api", "tool-script"]
TEMPLATES = ["default", "fintech-dapp"]


# -------- 通用小工具 --------

def prompt_if_missing(value, prompt_text, default=None, choices=None):
    if value:
        return value
    while True:
        if default is not None:
            raw = input(f"{prompt_text} [{default}]: ").strip()
            if not raw:
                raw = default
        else:
            raw = input(f"{prompt_text}: ").strip()

        if choices and raw not in choices:
            print(f"请输入有效选项: {choices}")
            continue
        if raw:
            return raw


def write_file(path: Path, content: str, overwrite: bool = False):
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# -------- 目录结构 --------

def create_common_dirs(project_root: Path):
    for d in ["docs", "tests", "scripts", "infra"]:
        (project_root / d).mkdir(parents=True, exist_ok=True)


def create_type_dirs(project_root: Path, project_type: str):
    src_root = project_root / "src"
    src_root.mkdir(exist_ok=True)

    if project_type == "web-app":
        for d in ["frontend", "backend", "shared"]:
            (src_root / d).mkdir(parents=True, exist_ok=True)
        (project_root / "tests" / "frontend").mkdir(parents=True, exist_ok=True)
        (project_root / "tests" / "backend").mkdir(parents=True, exist_ok=True)

    elif project_type == "service-api":
        for d in ["app", "core", "adapters"]:
            (src_root / d).mkdir(parents=True, exist_ok=True)

    elif project_type == "tool-script":
        for d in ["cli", "core"]:
            (src_root / d).mkdir(parents=True, exist_ok=True)


# -------- 根部文件 --------

def init_readme(project_root: Path, project_name: str, project_cn_name: str,
                project_type: str, template: str):
    readme_path = project_root / "README.md"
    content = dedent(f"""
    # {project_cn_name} ({project_name})

    项目类型：**{project_type}**
    使用模板：**{template}**

    ## 简介

    > 在这里用 2-3 句话描述这个项目解决什么问题，服务谁。

    ## 快速开始

    ```bash
    # TODO: 填写项目初始化和启动命令
    ```

    ## 目录结构（初始）

    - `docs/`: 项目文档（需求、Roadmap、决策记录等）
    - `src/`: 源码
    - `tests/`: 测试
    - `scripts/`: 脚本、自动化任务
    - `infra/`: 部署、运维相关配置
    """).strip() + "\n"
    write_file(readme_path, content)


def init_env_example(project_root: Path):
    env_path = project_root / ".env.example"
    content = dedent("""
    # 环境变量示例（根据项目需要补充）

    # APP_ENV=development
    # APP_DEBUG=true
    """).strip() + "\n"
    write_file(env_path, content)


def init_license(project_root: Path):
    license_path = project_root / "LICENSE"
    content = dedent("""
    MIT License (简化占位，按需替换为完整协议)

    Copyright (c) {year}
    """.format(year=datetime.now().year)).strip() + "\n"
    write_file(license_path, content)


def init_changelog(project_root: Path):
    changelog_path = project_root / "CHANGELOG.md"
    today = datetime.now().strftime("%Y-%m-%d")
    content = dedent(f"""
    # Changelog

    ## {today}
    - 项目通过脚手架初始化。
    """).strip() + "\n"
    write_file(changelog_path, content)


# -------- docs 模板 --------

def init_docs(project_root: Path, meta: dict):
    docs_root = project_root / "docs"

    brief = dedent(f"""
    # Project Brief - {meta['project_cn_name']} ({meta['project_name']})

    ## 1. 项目一句话介绍
    > 用一两句话说明项目要解决的核心问题。

    ## 2. 唯一成功指标（ONE metric）
    - 例：30 天内获取 30 个真实用户试用 / 完成 10 笔真实交易 / 录入 100 条数据 等

    ## 3. 目标用户
    - 地区：
    - 年龄段：
    - 职业 / 身份：
    - 使用场景：

    ## 4. 不做什么（反边界）
    - 本期明确不做的功能/范围，避免越做越散。

    ## 5. MVP 要验证的核心假设
    1. 
    2. 

    ## 6. 预估周期 & 时间投入
    - 预估周期：{meta['duration_weeks']} 周
    - 每周可投入时间：{meta['hours_per_week']} 小时

    ## 7. 风险清单（TOP 3）
    1. 
    2. 
    3. 
    """).strip() + "\n"
    write_file(docs_root / "project-brief.md", brief)

    roadmap = dedent("""
    # Roadmap

    > 只规划到 MVP，后续根据反馈再扩展。

    ## Milestone 概览

    - M1：可点击 Demo（预计 1-2 周）
    - M2：第一批真实用户测试（预计 2-4 周）
    - M3：对外发布 & 迭代（可选）

    ---

    ## M1 - 可点击 Demo

    ### 1. 核心流程
    - [ ] 

    ### 2. 数据 & 配置
    - [ ] 

    ### 3. 运营 & 基础统计 / 埋点
    - [ ] 

    ---

    ## M2 - 真实用户测试

    ### 1. 用户入口 & 注册 / 登录（如需要）
    - [ ] 

    ### 2. 关键行为闭环
    - [ ] 

    ### 3. 反馈收集
    - [ ] 

    ---

    ## M3 - 对外发布 / 迭代（可选）

    - [ ] 
    """).strip() + "\n"
    write_file(docs_root / "roadmap.md", roadmap)

    today = datetime.now().strftime("%Y-%m-%d")
    devlog = dedent(f"""
    # Dev Log

    > 每天用 3 行记录进展，便于回顾和复盘。

    ## {today}
    - 今天完成：
      - 项目初始化（脚手架创建目录与文档）
    - 遇到问题：
      - 暂无
    - 明天最重要的一件事：
      - 完成最小运行环境 / Hello World
    """).strip() + "\n"
    write_file(docs_root / "dev-log.md", devlog)

    decisions = dedent("""
    # Decisions Log

    > 记录重要架构 / 技术 / 业务决策，方便将来回顾。

    ## YYYY-MM-DD - [决策标题示例]
    - 背景：
    - 选项：
    - 最终选择：
    - 原因：
    - 影响：
    """).strip() + "\n"
    write_file(docs_root / "decisions.md", decisions)


# -------- 模板: fintech-dapp --------

def apply_fintech_dapp_template(project_root: Path, project_type: str, meta: dict):
    src_root = project_root / "src"

    frontend_root = src_root / "frontend"
    backend_root = src_root / "backend"

    if frontend_root.exists():
        for d in ["pages", "components", "hooks", "styles"]:
            (frontend_root / d).mkdir(parents=True, exist_ok=True)

        frontend_readme = dedent("""
        # Frontend 结构（fintech-dapp 模板）

        - `pages/`: 页面级组件（路由对应）
        - `components/`: 可复用 UI 组件
        - `hooks/`: 自定义 hooks（如钱包连接、行情轮询）
        - `styles/`: 全局样式 / Tailwind 配置等
        """).strip() + "\n"
        write_file(frontend_root / "README.md", frontend_readme)

    if backend_root.exists():
        for d in ["api", "services", "models", "jobs"]:
            (backend_root / d).mkdir(parents=True, exist_ok=True)

        backend_readme = dedent("""
        # Backend 结构（fintech-dapp 模板）

        - `api/`: 对外暴露的接口（REST / GraphQL 等）
        - `services/`: 业务服务层（撮合、风控、账户等）
        - `models/`: 数据模型 / ORM
        - `jobs/`: 定时任务（清算、统计、同步链上数据等）
        """).strip() + "\n"
        write_file(backend_root / "README.md", backend_readme)

    infra_root = project_root / "infra"
    docker_example = dedent("""
    version: "3.9"

    services:
      backend:
        image: backend-image-placeholder
        container_name: backend
        restart: unless-stopped
        env_file:
          - ../.env
        ports:
          - "8000:8000"

      frontend:
        image: frontend-image-placeholder
        container_name: frontend
        restart: unless-stopped
        ports:
          - "3000:3000"
        environment:
          - API_BASE_URL=http://backend:8000

      db:
        image: postgres:16
        container_name: db
        restart: unless-stopped
        environment:
          - POSTGRES_USER=app
          - POSTGRES_PASSWORD=app
          - POSTGRES_DB=app
        volumes:
          - db_data:/var/lib/postgresql/data

    volumes:
      db_data:
    """).strip() + "\n"
    write_file(infra_root / "docker-compose.example.yml", docker_example)

    fintech_doc = dedent(f"""
    # Fintech / Dapp 项目说明（模板自动生成）

    项目：{meta['project_cn_name']} ({meta['project_name']})

    ## 1. 产品定位

    - 目标用户：
    - 使用场景：
    - 解决什么核心问题：

    ## 2. 关键业务概念

    - 账户体系：
    - 资产类型（现金 / 合约 / 积分 / 链上资产 等）：
    - 交易品种：
    - 手续费 / 点差：

    ## 3. 合规 & 风控注意事项（思考框架）

    - 用户身份（KYC）：
    - 资金来源合规性：
    - 风险提示机制：
    - 风控规则（限额、风控阈值等）：

    ## 4. 技术要点（待补充）

    - 钱包 / 支付渠道：
    - 行情数据源：
    - 撮合或定价模式：
    - 日志与监控：
    """).strip() + "\n"
    write_file(project_root / "docs" / "fintech-notes.md", fintech_doc)


def apply_template(project_root: Path, project_type: str, template: str, meta: dict):
    if template == "fintech-dapp":
        apply_fintech_dapp_template(project_root, project_type, meta)
    # default 模板就不做额外动作


# -------- Meta & Git --------

def write_project_meta(project_root: Path, meta: dict):
    meta_path = project_root / "project_meta.json"
    meta_to_save = {
        **meta,
        "created_at": datetime.now().isoformat(),
        "scaffold_version": "2.0",
    }
    write_file(meta_path, json.dumps(meta_to_save, ensure_ascii=False, indent=2) + "\n", overwrite=True)


def git_init(project_root: Path):
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        print("⚠️ 未检测到 git，跳过 git 初始化。")
        return

    if (project_root / ".git").exists():
        print("ℹ️ 该目录已是 git 仓库，跳过 git init。")
        return

    try:
        subprocess.run(["git", "init"], cwd=str(project_root), check=True)
        subprocess.run(["git", "add", "."], cwd=str(project_root), check=True)
        subprocess.run(
            ["git", "commit", "-m", "chore: init project from scaffold v2"],
            cwd=str(project_root),
            check=True,
        )
        print("✅ 已完成 git 初始化并创建初始提交。")
    except Exception as e:
        print(f"⚠️ git 初始化失败：{e}")


# -------- CLI --------

def parse_args():
    parser = argparse.ArgumentParser(description="单兵项目脚手架工具 v2")
    parser.add_argument("project_name", nargs="?", help="项目英文机器名，例如 fintech-x-app-202511")
    parser.add_argument("--type", "-t", dest="project_type", choices=PROJECT_TYPES, help="项目类型")
    parser.add_argument("--cn-name", dest="project_cn_name", help="项目中文名")
    parser.add_argument(
        "--template",
        dest="template",
        choices=TEMPLATES,
        help=f"脚手架模板，默认 default，可选: {TEMPLATES}",
    )
    parser.add_argument("--base-dir", dest="base_dir", help="项目创建基础目录，默认当前目录")
    parser.add_argument("--no-git", action="store_true", help="不自动初始化 git 仓库")
    return parser.parse_args()


def main():
    args = parse_args()

    project_name = prompt_if_missing(
        args.project_name,
        "请输入项目英文机器名 (如 fintech-x-app-202511)"
    )
    project_cn_name = prompt_if_missing(
        args.project_cn_name,
        "请输入项目中文名",
        default=project_name
    )
    project_type = prompt_if_missing(
        args.project_type,
        f"请选择项目类型 {PROJECT_TYPES}",
        choices=PROJECT_TYPES
    )
    template = prompt_if_missing(
        args.template,
        f"请选择模板 {TEMPLATES}",
        default="default",
        choices=TEMPLATES
    )

    base_dir = args.base_dir or os.getcwd()
    duration_weeks = prompt_if_missing(None, "预估项目周期（周）", default="4")
    hours_per_week = prompt_if_missing(None, "每周可投入时间（小时）", default="20")

    project_root = Path(base_dir).expanduser().resolve() / project_name

    if project_root.exists() and any(project_root.iterdir()):
        print(f"⚠️ 目标目录已存在且非空：{project_root}")
        confirm = input("继续可能覆盖部分文件，是否继续？(y/N): ").strip().lower()
        if confirm != "y":
            print("已取消。")
            return

    project_root.mkdir(parents=True, exist_ok=True)

    meta = {
        "project_name": project_name,
        "project_cn_name": project_cn_name,
        "project_type": project_type,
        "template": template,
        "duration_weeks": duration_weeks,
        "hours_per_week": hours_per_week,
    }

    # 1. 通用目录
    create_common_dirs(project_root)
    # 2. 类型目录
    create_type_dirs(project_root, project_type)
    # 3. 根部文件
    init_readme(project_root, project_name, project_cn_name, project_type, template)
    init_env_example(project_root)
    init_license(project_root)
    init_changelog(project_root)
    # 4. docs 模板
    init_docs(project_root, meta)
    # 5. 模板特化逻辑
    apply_template(project_root, project_type, template, meta)
    # 6. meta 信息
    write_project_meta(project_root, meta)
    # 7. git 初始化
    if not args.no_git:
        git_init(project_root)

    print("\n🎉 脚手架已完成项目初始化：")
    print(f"   位置：{project_root}")
    print(f"   类型：{project_type}")
    print(f"   模板：{template}")
    print("   下一步建议：")
    print("   1. 打开 docs/project-brief.md 补全项目信息")
    if template == "fintech-dapp":
        print("   2. 查看 docs/fintech-notes.md，把业务关键点先写清楚")
    else:
        print("   2. 在 docs/roadmap.md 写出 M1 要完成的具体项")
    print("   3. 决定技术栈并开始搭建最小运行环境（Hello World）")

