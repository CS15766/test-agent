# 铁路调度Agent系统

基于Qwen大模型和整数规划的智能铁路调度优化系统。

## 系统架构

```
railway_dispatch/
├── data/                     # 数据层
│   ├── trains.json          # 列车时刻表
│   ├── stations.json        # 车站数据
│   └── scenarios/           # 场景数据
├── evaluation/              # 评估层
│   └── evaluator.py        # 方案评估
├── models/                  # 数据模型层
│   ├── data_models.py      # Pydantic模型
│   └── data_loader.py      # 数据加载器
├── qwen/                    # Qwen Agent层
│   ├── qwen_agent.py       # Qwen Agent核心
│   ├── tool_registry.py    # MCP Tools注册表
│   └── prompts.py          # Prompt模板
├── rules/                   # 约束规则层
│   └── validator.py        # 规则验证器
├── skills/                  # Skills层
│   └── dispatch_skills.py  # 调度Skills
├── solver/                  # 求解器层
│   └── mip_scheduler.py    # MIP整数规划求解器
├── visualization/           # 可视化层
│   └── simple_diagram.py   # 运行图生成
└── web/                     # Web层
    └── app.py              # Flask Web应用
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Web服务

```bash
python3 web/app.py
```

### 3. 访问系统

打开浏览器访问: http://localhost:8080

## 核心功能

### 智能调度
- **自然语言输入**: 用自然语言描述调度需求，Agent自动识别场景
- **表单输入**: 传统表单方式配置延误场景
- **场景识别**: 自动识别临时限速、突发故障等场景
- **整数规划优化**: 使用MIP求解器生成最优调度方案

### Agent能力
- 基于Qwen大模型的场景理解
- MCP/Skills模式的功能调用
- 详细的推理过程输出

### 可视化
- 优化后时刻表展示
- 运行图对比

## 核心模块

### 1. Qwen Agent (`qwen/`)
- `qwen_agent.py`: Agent核心，场景识别和功能调用
- `tool_registry.py`: Tools注册和执行
- `prompts.py`: Prompt模板

### 2. MIP求解器 (`solver/mip_scheduler.py`)
- 混合整数规划模型
- 追踪间隔约束
- 站台占用约束

### 3. Skills (`skills/dispatch_skills.py`)
- `TemporarySpeedLimitSkill`: 临时限速场景
- `SuddenFailureSkill`: 突发故障场景

### 4. 数据模型 (`models/`)
- `data_models.py`: Pydantic模型定义
- `data_loader.py`: 统一数据加载器

## 使用示例

### 自然语言调度
```
输入: G1001列车在天津西站延误10分钟，需要进行调度优化

输出:
- 场景识别: temporary_speed_limit
- 选择技能: temporary_speed_limit_skill
- 最大延误: 10分钟
- 运行图对比
```

## 技术栈

- **大模型**: Qwen (ModelScope)
- **求解器**: PuLP (整数规划)
- **Web框架**: Flask
- **数据验证**: Pydantic
- **可视化**: Matplotlib

## 版本

- v2.0: 新增Qwen Agent智能调度
- v1.1: 新增统一数据加载器、约束规则验证器
- v1.0: 初版，支持临时限速和突发故障场景

## 许可证

MIT License
