# 企业 / 高校知识库 Agent（Vue 3 + LangChain + Milvus）

基于 RAG（检索增强生成）的知识库问答系统：上传文档后自动解析、切片、向量化入库，提问时走「混合检索 → 上下文组装 → LLM 流式生成 → 引用溯源」链路，前端以打字机效果展示答案并附引用来源。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Element Plus + Vue Router |
| 后端 | Python + FastAPI + LangChain（`langchain-openai` / `langchain-milvus`） |
| 向量库 | Milvus Standalone（Docker，含 etcd、MinIO；Attu 可视化台） |
| 元数据 | SQLite（标准库，零额外服务） |
| 模型 | 任意 **OpenAI 兼容接口** 的 Chat 与 Embedding（豆包方舟 / DeepSeek / 硅基流动 / vLLM 等） |

## 目录结构

```text
.
├── docker-compose.yml          # Milvus + etcd + MinIO + Attu
├── backend/
│   ├── .env.example            # 复制为 .env 后填写接口地址与密钥
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI 入口、CORS、健康检查
│       ├── core/config.py      # .env 配置
│       ├── ingestion/          # 离线流水线：loader 解析、pipeline 切片入库
│       ├── retrieval/          # Embedding 与 Milvus 向量库单例
│       ├── agent/chain.py      # RAG Prompt 与 LLM
│       ├── api/chat.py         # POST /api/chat（SSE 流式）
│       ├── api/docs.py         # 文档上传 / 列表 / 删除
│       ├── db/metadata.py      # SQLite 文档元数据
│       └── schemas/            # Pydantic 模型
└── frontend/
    └── src/
        ├── api/                # axios 文档接口 + fetch-event-source 流式问答
        ├── views/ChatView.vue  # 对话页
        ├── views/DocsView.vue  # 知识库管理页
        └── components/SourceCard.vue  # 引用来源卡片
```

## 快速开始（三步）

### 1. 启动 Milvus

```powershell
docker compose up -d
```

- Milvus gRPC：`http://localhost:19530`
- Attu 可视化台：<http://localhost:3000>（连接地址填 `milvus:19530`）

### 2. 启动后端

```powershell
cd backend
.\run.ps1
```

`run.ps1` 首次运行会自动创建虚拟环境并安装依赖；若尚未配置 `.env`，会自动从 `.env.example` 复制一份并退出，此时编辑 `.env` 填入 LLM / Embedding 的地址、密钥、模型名后，再次执行 `.\run.ps1` 即可。

<details>
<summary>手动启动方式（不用脚本）</summary>

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # 编辑 .env
uvicorn app.main:app --reload --port 8000
```
</details>

- 接口文档（Swagger）：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/api/health>（Milvus 未启动时会显示 degraded）

`.env` 关键项（以豆包方舟为例，DeepSeek 把 base_url 换成 `https://api.deepseek.com/v1`）：

```ini
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_API_KEY=sk-xxx
LLM_MODEL=你的对话模型ID
EMBEDDING_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_MODEL=你的向量模型ID
```

> 注意：DeepSeek 官方不提供 Embedding 接口，Embedding 需要选豆包 / 硅基流动（BGE 系列）/ OpenAI 等提供方。
> Embedding 维度在首次写入时固定到 Milvus 集合，**更换不同维度的向量模型需改 `MILVUS_COLLECTION` 或在 Attu 中删集合重建**。

### 3. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

> 若项目路径含空格或 `&`（如本项目 `Enterprise & Academic ...`），`npm run` 在部分 Windows 环境会被 cmd 截断路径而报错，改用等价脚本 `.\dev.ps1`（构建用 `.\build.ps1`）。

打开 <http://localhost:5173>：先在「知识库管理」上传 PDF/TXT/MD/DOCX，再到「智能问答」提问。

## SSE 事件协议（前端已实现）

```text
event: sources  data: {"sources":[{"index":1,"source":"...","snippet":"..."}]}
event: token    data: {"content":"增量文本"}
event: done     data: {}
event: error    data: {"message":"..."}
```

## 常见问题

1. **`npm run dev` 报 `'Academic' is not recognized` / `Cannot find module ...\vite.js`**：项目路径含 `&`，cmd 截断了路径。用 `.\dev.ps1` 启动、`.\build.ps1` 构建。
2. **`MilvusException` / health degraded**：Milvus 容器首次启动需要 30~90 秒初始化，等 `docker compose ps` 中 standalone 变为 healthy 再试。
3. **Embedding 报 401 / model not found**：检查 `.env` 中 base_url、key、模型名；Chat 与 Embedding 可以用不同提供方。
4. **上传扫描版 PDF 提示无文本**：当前解析器只抽文本层，扫描件需要后续接入 OCR（如 PaddleOCR）。
5. **Windows 下 venv 激活被拦截**：直接用 `.\run.ps1`，或手动调用 `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`。

## 后续演进路线

- [ ] 混合检索：BM25 关键词 + 向量（Milvus 2.5 原生 Hybrid Search）
- [ ] Rerank 精排（BGE-Reranker），显著提升 Top-K 准确率
- [ ] 查询改写 / 多查询（Multi-Query）、对话历史压缩
- [ ] 升级为 LangGraph Agent：工具调用（查课表/工单/内部系统）、多步规划
- [ ] RBAC 权限感知检索（企业：部门隔离；高校：院系/课程空间）
- [ ] 评估体系：召回率、答案忠实度、引用命中率
- [ ] 生产部署：FastAPI 多副本 + Milvus Cluster + K8s
