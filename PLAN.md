# GenReader 项目实施计划

> AI 驱动的 PDF / 图像文本识别与坐标定位系统
> 基于视觉大模型（VLM），支持多用户并发、异步队列、批量处理

---

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 技术栈](#2-技术栈)
- [3. 整体架构](#3-整体架构)
- [4. 目录结构](#4-目录结构)
- [5. 实施步骤](#5-实施步骤)
- [6. 里程碑](#6-里程碑)
- [7. 风险与注意事项](#7-风险与注意事项)

---

## 1. 项目概述

### 1.1 功能目标

- 用户上传 **PDF / PNG / JPG** 等文档
- 指定需要识别的文本（关键词或自然语言描述）
- 系统返回匹配文本的 **精确坐标**（bbox），前端可高亮渲染
- 支持 **多用户并发** 与 **大批量文件** 排队处理
- 全量 **Docker / docker-compose** 一键部署

### 1.2 核心能力

| 能力 | 说明 |
|---|---|
| 视觉大模型 OCR | 调用 GPT-4V / Qwen-VL / InternVL 等 VLM，结合传统 OCR 做兜底 |
| 坐标归一化 | 统一 bbox 格式（`[x, y, w, h]`，归一化 0-1），兼容多引擎 |
| 异步任务队列 | Redis + arq，支持高/默认/批量多级队列 |
| 进度实时推送 | WebSocket / SSE，避免前端轮询 |
| 多格式支持 | PDF 自动拆页 fan-out、图像直接处理 |
| 配额与限流 | IP 限流 + 用户级配额，防止滥用 |

---

## 2. 技术栈

### 2.1 后端

| 类别 | 选型 | 版本 |
|---|---|---|
| 语言 | Python | 3.11 |
| Web 框架 | FastAPI | latest |
| 异步任务 | arq (Redis-based) | latest |
| ORM | SQLAlchemy 2.x (async) | latest |
| 迁移 | Alembic | latest |
| 数据库 | PostgreSQL | 16 |
| 缓存/队列 | Redis | 7 |
| 对象存储 | MinIO（S3 兼容） | latest |
| 配置 | pydantic-settings | latest |
| 测试 | pytest + pytest-asyncio | latest |
| 包管理 | uv 或 poetry | - |

### 2.2 前端

| 类别 | 选型 | 版本 |
|---|---|---|
| 语言 | TypeScript | 5.x |
| 框架 | Next.js (App Router) | 16.2.2 |
| UI 库 | React | 19.x |
| 样式 | TailwindCSS | 4.x |
| 组件库 | shadcn/ui | latest |
| 状态管理 | Zustand 或 TanStack Query | latest |
| PDF 渲染 | pdf.js / react-pdf | latest |
| 图像标注 | konva / fabric.js | latest |

### 2.3 基础设施

- Docker + docker-compose
- Nginx（反向代理，生产环境）
- GitHub Actions（CI/CD，可选）

---

## 3. 整体架构

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │◄────►│   FastAPI    │◄────►│ PostgreSQL  │
│  (frontend) │      │  (backend)   │      │             │
└──────┬──────┘      └──────┬───────┘      └─────────────┘
       │                    │
       │ WebSocket          │ enqueue
       │                    ▼
       │             ┌──────────────┐      ┌─────────────┐
       └────────────►│    Redis     │◄────►│  arq Worker │
                     │ (queue+pub)  │      │ (fast/batch)│
                     └──────────────┘      └──────┬──────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │  VLM API    │
                                           │ (GPT-4V...) │
                                           └─────────────┘
                     ┌──────────────┐
                     │    MinIO     │◄─── 文件存储
                     └──────────────┘
```

### 3.1 请求流程

1. 前端上传文件 → `POST /api/v1/ocr` → 文件存入 MinIO
2. 后端创建任务记录 → 入 Redis 队列 → 立即返回 `task_id`
3. 前端跳转任务详情页 → WebSocket 订阅 `task:{id}`
4. Worker 消费队列 → 调用 VLM → 写结果到 DB → publish 进度
5. 前端收到 `SUCCESS` → 拉结果 → 渲染 bbox 高亮

### 3.2 大 PDF Fan-out

```
pdf_split_task(pdf)
  ├─ ocr_task(page_1)  ─┐
  ├─ ocr_task(page_2)   ├─► merge_task → 写 DB → notify
  └─ ocr_task(page_N)  ─┘
```

---

## 4. 目录结构

```
genreader/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── core/                   # 基础设施
│   │   │   ├── config.py           # 环境变量配置
│   │   │   ├── security.py         # JWT / CORS
│   │   │   ├── logging.py          # 日志
│   │   │   ├── exceptions.py       # 自定义异常
│   │   │   ├── rate_limit.py       # IP 限流
│   │   │   └── quota.py            # 用户配额
│   │   ├── api/
│   │   │   ├── deps.py             # 依赖注入
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   │           ├── ocr.py      # OCR 上传入队
│   │   │           ├── files.py    # 文件管理
│   │   │           ├── tasks.py    # 任务状态查询
│   │   │           └── ws.py       # WebSocket 推送
│   │   ├── schemas/                # Pydantic DTO
│   │   │   ├── ocr.py
│   │   │   ├── file.py
│   │   │   └── task.py
│   │   ├── models/                 # SQLAlchemy ORM
│   │   │   ├── base.py
│   │   │   ├── file.py
│   │   │   └── ocr_record.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── init_db.py
│   │   ├── crud/                   # 数据库 CRUD
│   │   │   ├── base.py
│   │   │   ├── file.py
│   │   │   └── ocr_record.py
│   │   ├── services/               # 业务逻辑
│   │   │   ├── ocr_service.py
│   │   │   ├── file_service.py
│   │   │   ├── pdf_service.py
│   │   │   └── task_service.py
│   │   ├── ml/                     # 大模型封装
│   │   │   ├── base.py             # 抽象接口
│   │   │   ├── vlm_client.py       # VLM 客户端
│   │   │   ├── ocr_engine.py       # 传统 OCR 兜底
│   │   │   └── coord_utils.py      # 坐标工具
│   │   ├── workers/
│   │   │   ├── arq_worker.py       # Worker 入口
│   │   │   ├── queues.py           # 队列定义
│   │   │   └── tasks/
│   │   │       ├── ocr_task.py
│   │   │       ├── pdf_split_task.py
│   │   │       └── merge_task.py
│   │   └── utils/
│   │       ├── image.py
│   │       └── storage.py          # MinIO/本地存储抽象
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── api/
│   │   ├── services/
│   │   └── ml/
│   ├── scripts/
│   ├── storage/                    # 本地开发文件目录
│   ├── .env.example
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # 首页
│   │   │   ├── upload/
│   │   │   │   └── page.tsx        # 上传页
│   │   │   ├── tasks/
│   │   │   │   ├── page.tsx        # 任务列表
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx    # 任务详情 + 结果渲染
│   │   │   └── api/                # Next.js Route Handlers（如需）
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn 组件
│   │   │   ├── upload/             # 上传组件
│   │   │   ├── viewer/             # PDF/图像查看器 + bbox 标注
│   │   │   └── task/               # 任务卡片、进度条
│   │   ├── lib/
│   │   │   ├── api.ts              # API 客户端
│   │   │   ├── ws.ts               # WebSocket 封装
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   │   ├── useTask.ts
│   │   │   └── useUpload.ts
│   │   ├── stores/                 # Zustand stores
│   │   └── types/                  # TS 类型定义
│   ├── public/
│   ├── .env.local.example
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── Dockerfile
│   └── README.md
│
├── docker-compose.yml              # 开发环境
├── docker-compose.prod.yml         # 生产环境
├── .gitignore
├── PLAN.md                         # 本文件
└── README.md                       # 项目总 README
```

---

## 5. 实施步骤

### Phase 0 — 项目初始化

- [ ] 创建 `backend/` 与 `frontend/` 目录骨架
- [ ] 初始化 git 仓库 + `.gitignore`
- [ ] 编写项目总 `README.md`（含徽章头）
- [ ] 搭建 `docker-compose.yml` 基础服务（postgres / redis / minio）

### Phase 1 — 后端基础设施

- [ ] `pyproject.toml` 配置依赖（FastAPI / SQLAlchemy / arq / pydantic-settings）
- [ ] `core/config.py` 加载 `.env`
- [ ] `db/session.py` 建立 async engine
- [ ] `models/` 定义 `File`、`OCRRecord` 表
- [ ] Alembic 初始化 + 首次迁移
- [ ] `main.py` 挂载路由、CORS、异常处理
- [ ] 编写 `Dockerfile`（多阶段构建）
- [ ] 健康检查接口 `/health`

### Phase 2 — 文件上传与存储

- [ ] `utils/storage.py` 抽象存储接口（本地 / MinIO 双实现）
- [ ] `services/file_service.py` 文件校验、去重（md5）、保存
- [ ] `api/v1/endpoints/files.py` 上传/下载路由
- [ ] `schemas/file.py` 定义 DTO
- [ ] 单元测试覆盖

### Phase 3 — OCR 核心与 ML 层

- [ ] `ml/base.py` 定义 `OCREngine` 抽象接口
- [ ] `ml/vlm_client.py` 实现 VLM 调用（优先 OpenAI SDK 兼容接口）
- [ ] `ml/ocr_engine.py` 接入 PaddleOCR 或 Tesseract 作为兜底
- [ ] `ml/coord_utils.py` bbox 归一化、坐标系转换
- [ ] `services/ocr_service.py` 编排：文件 → 引擎 → 结果合并
- [ ] `schemas/ocr.py` 定义 `BoundingBox`、`OCRResult`
- [ ] 单元测试（用 fixture 图像）

### Phase 4 — 队列与 Worker

- [ ] `workers/queues.py` 定义 `high / default / batch` 三级队列
- [ ] `workers/arq_worker.py` WorkerSettings 配置
- [ ] `workers/tasks/ocr_task.py` 单页/单图 OCR 任务
- [ ] `services/pdf_service.py` PDF 拆页
- [ ] `workers/tasks/pdf_split_task.py` Fan-out 大 PDF
- [ ] `workers/tasks/merge_task.py` 合并子任务结果
- [ ] 失败重试策略（`max_tries` + 指数退避）
- [ ] docker-compose 增加 `worker-fast` / `worker-batch` 服务

### Phase 5 — 任务管理与实时推送

- [ ] `services/task_service.py` 创建/查询/取消任务
- [ ] `api/v1/endpoints/ocr.py` 上传即入队，返回 `task_id`
- [ ] `api/v1/endpoints/tasks.py` 状态查询、结果拉取、取消
- [ ] `api/v1/endpoints/ws.py` WebSocket 订阅任务进度
- [ ] Worker 通过 Redis Pub/Sub 广播进度事件
- [ ] 任务状态机：`PENDING → QUEUED → PROCESSING → SUCCESS/FAILED/CANCELLED`

### Phase 6 — 限流与配额

- [ ] `core/rate_limit.py` 集成 slowapi（IP 级限流）
- [ ] `core/quota.py` Redis 计数器实现用户日配额
- [ ] 队列长度监控：超阈值返回 503
- [ ] Worker `max_jobs` 限制单机并发

### Phase 7 — 前端骨架

- [ ] `create-next-app` 初始化（TS + App Router + Tailwind）
- [ ] 接入 shadcn/ui、配置主题
- [ ] `lib/api.ts` 封装 fetch 客户端
- [ ] `lib/ws.ts` WebSocket 封装（自动重连）
- [ ] `types/` 从后端 schema 同步类型（或用 openapi-typescript）
- [ ] 全局布局 + 导航

### Phase 8 — 前端功能页面

- [ ] **首页**：产品介绍、快速开始
- [ ] **上传页**：拖拽上传、关键词输入、格式校验
- [ ] **任务列表页**：分页、状态筛选、重试按钮
- [ ] **任务详情页**：
  - PDF/图像查看器（react-pdf / konva）
  - bbox 高亮层
  - 进度条（WebSocket 实时更新）
  - 结果 JSON 导出

### Phase 9 — Docker 化与部署

- [ ] `backend/Dockerfile` 多阶段构建（依赖层缓存）
- [ ] `frontend/Dockerfile`（Next.js standalone 输出）
- [ ] `docker-compose.yml` 开发环境（含 hot-reload）
- [ ] `docker-compose.prod.yml` 生产环境 + Nginx
- [ ] 健康检查 + 重启策略
- [ ] `.env.example` 文档化所有环境变量

### Phase 10 — 测试、文档、收尾

- [ ] 后端测试覆盖率 ≥ 70%
- [ ] 前端关键组件测试（vitest + testing-library）
- [ ] E2E 测试（Playwright，可选）
- [ ] 编写 API 使用文档（FastAPI 自带 `/docs` 已覆盖大部分）
- [ ] 录制 Demo GIF / 截图
- [ ] 完善 README（安装、部署、贡献指南）

---

## 6. 里程碑

| 里程碑 | 内容 | 交付物 |
|---|---|---|
| **M1** | Phase 0-2 | 后端骨架 + 文件上传能跑通 |
| **M2** | Phase 3-4 | 单张图 OCR 跑通，能返回坐标 |
| **M3** | Phase 5-6 | 异步队列 + 并发控制完整 |
| **M4** | Phase 7-8 | 前端 MVP，端到端跑通 |
| **M5** | Phase 9-10 | 一键部署 + 文档完整，可发布 |

---

## 7. 风险与注意事项

### 7.1 技术风险

| 风险 | 影响 | 应对 |
|---|---|---|
| VLM 返回坐标不准 | 核心功能失效 | 双引擎兜底（VLM + 传统 OCR），坐标校准 |
| VLM API 限流/超时 | 任务失败率高 | arq 自动重试 + 多 Provider 切换 |
| 大 PDF 内存爆炸 | Worker OOM | 强制拆页 + 单 Worker `max_jobs=1` |
| WebSocket 断连 | 进度丢失 | REST 补偿查询 + 自动重连 |
| 显存/算力成本 | 成本不可控 | 配额 + 按文件大小计费策略 |

### 7.2 工程注意

- **坐标系统一**：PDF 原点在左下，图像在左上，前端渲染在左上 —— 必须在 `coord_utils` 里统一转换
- **文件去重**：同一 md5 的文件只存一份，节省存储
- **敏感信息**：不要把用户文件日志里打印出来
- **CORS**：开发环境放开，生产环境严格白名单
- **数据库连接池**：async engine 的 `pool_size` 要和 worker 数匹配
- **Redis 持久化**：队列数据建议开 AOF，避免重启丢任务

### 7.3 待决策项

- [ ] 是否需要用户系统（登录/注册）？MVP 阶段可先用 API Key
- [ ] VLM 选型：OpenAI / Anthropic / 本地 Qwen-VL？成本 vs 效果
- [ ] 结果保留期限：多久后清理已完成任务的文件？
- [ ] 是否支持 Webhook 回调（而非只有 WebSocket）？

---

_Last updated: 2026-04-15_
