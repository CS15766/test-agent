# 铁路调度Agent系统架构设计文档

## 文档概述

基于Qwen大模型和整数规划的智能铁路调度Agent系统。

**设计约束**：
- 部署规模：小规模（<10站，<20车）
- 建模方法：整数规划（MIP）
- Web框架：Flask
- 大模型：Qwen (ModelScope)

---

## 1. 系统整体架构

### 1.1 架构分层设计

```
┌─────────────────────────────────────────────────────────┐
│                     数据层 (data/)                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  数据模型层 (models/)                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Qwen Agent层 (qwen/) + Agent层             │
│  场景识别、延误分析、Skill选择、功能调用                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Skills层 (skills/)                      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  求解器层 (solver/)                      │
│  MIPScheduler: 混合整数规划求解                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  可视化层 (visualization/)               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Web层 (web/)                          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 工作流设计

```
用户输入（自然语言或表单）
       ↓
QwenAgent.analyze()
       ↓
场景识别 + Tool选择
       ↓
执行Skill (MIP求解)
       ↓
返回调度方案
       ↓
展示时刻表 + 运行图
```

---

## 2. 核心模块

### 2.1 Qwen Agent

```python
from qwen.qwen_agent import create_qwen_agent

agent = create_qwen_agent()
result = agent.analyze(delay_injection)
print(result.reasoning)  # Agent推理过程
```

### 2.2 MIP求解器

```python
from solver.mip_scheduler import MIPScheduler

scheduler = MIPScheduler(trains, stations)
result = scheduler.solve(delay_injection, objective="min_max_delay")
```

### 2.3 Skills

| Skill | 场景类型 | 说明 |
|-------|---------|------|
| TemporarySpeedLimitSkill | 临时限速 | 处理限速导致的多车延误 |
| SuddenFailureSkill | 突发故障 | 处理单车故障延误 |

---

## 3. 数据模型

### 3.1 核心类型

- `Train`: 列车时刻表
- `Station`: 车站信息
- `DelayInjection`: 延误注入数据

### 3.2 场景类型

- `temporary_speed_limit`: 临时限速
- `sudden_failure`: 突发故障
- `section_interrupt`: 区间中断（预留）

---

## 4. 约束规则

### 4.1 延误等级分类

| 等级 | 标识 | 延误时间范围 |
|------|------|-------------|
| 微小 | MICRO | [0, 5) 分钟 |
| 小 | SMALL | [5, 30) 分钟 |
| 中 | MEDIUM | [30, 100) 分钟 |
| 大 | LARGE | [100, +∞) 分钟 |

### 4.2 约束常量

| 约束类型 | 默认值 |
|---------|--------|
| 追踪间隔 | 600秒 |
| 站台占用 | 300秒 |

---

## 5. API接口

### 5.1 智能调度

```
POST /api/agent_chat
Body: { "prompt": "G1001延误10分钟..." }
Response: { "success": true, "reasoning": "...", "delay_statistics": {...} }
```

### 5.2 表单调度

```
POST /api/dispatch
Body: { "scenario_type": "temporary_speed_limit", ... }
```

---

## 6. 文件结构

```
railway_dispatch/
├── agent/planner_agent.py      # 规则Agent
├── data/                       # 数据文件
├── models/                     # 数据模型
├── qwen/                       # Qwen Agent
│   ├── qwen_agent.py
│   ├── tool_registry.py
│   └── prompts.py
├── skills/dispatch_skills.py   # Skills
├── solver/mip_scheduler.py     # MIP求解器
├── visualization/              # 可视化
└── web/app.py                  # Web应用
```
