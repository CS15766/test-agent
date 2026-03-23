# Qwen Agent 基于MCP/Skills的场景识别与功能调用规范

## 1. 需求概述

基于千问模型(Qwen3-8B)实现铁路调度Agent，实现：
1. **场景识别**：分析延误注入数据，识别场景类型（临时限速/突发故障/区间中断）
2. **功能调用**：基于MCP/Skills模式选择并调用对应的调度技能
3. **结果返回**：执行调度优化并返回结果

**重要**：调度方案使用**纯数学的整数规划方法**（已在`mip_scheduler.py`中实现）

## 2. 现有功能基础

### 已实现模块（不可更改）

| 模块 | 路径 | 功能 |
|------|------|------|
| **MIP求解器** | `solver/mip_scheduler.py` | 纯数学整数规划求解（PuLP） |
| **Skills** | `skills/dispatch_skills.py` | TemporarySpeedLimitSkill, SuddenFailureSkill |
| **Planner Agent** | `agent/planner_agent.py` | 基于规则的场景识别（基准） |
| **数据模型** | `models/data_models.py` | DelayInjection, Train, Station等 |

### 现有Skills接口

```python
# skills/dispatch_skills.py
class BaseDispatchSkill:
    name: str
    description: str
    
    def execute(
        self,
        train_ids: List[str],
        station_codes: List[str],
        delay_injection: Dict[str, Any],
        optimization_objective: str = "min_max_delay"
    ) -> DispatchSkillOutput:
        """执行调度Skill"""
        pass

# 可用Skills
skills = {
    "temporary_speed_limit_skill": TemporarySpeedLimitSkill(scheduler),
    "sudden_failure_skill": SuddenFailureSkill(scheduler),
    "section_interrupt_skill": SectionInterruptSkill(scheduler)
}
```

## 3. 技术方案

### 3.1 模型调用
- 使用ModelScope加载本地Qwen3-8B模型
- 路径：`/Users/chenshuai18/.cache/modelscope/hub/models/Qwen/Qwen3___5-0___8B`
- 采用chat template构建对话

### 3.2 MCP/Skills Function Calling
参考OpenAI Function Calling和LangChain Tools模式：
1. 将Skills封装为JSON Schema格式的工具定义
2. 在System Prompt中注入工具描述
3. 解析模型输出，提取函数名和参数
4. 执行对应的Skill函数（MIP求解）
5. 将执行结果返回模型进行总结

### 3.3 数据流设计

```
用户输入 (DelayInjection JSON)
       ↓
QwenAgent.analyze()
       ↓
场景识别Prompt + Tools定义
       ↓
Qwen模型推理 → 输出Tool Call
       ↓
解析: tool_name="temporary_speed_limit_skill", args={...}
       ↓
ToolRegistry.execute(tool_name, args)
       ↓
MIPScheduler.solve() ← 纯数学整数规划
       ↓
DispatchSkillOutput
       ↓
返回最终调度方案
```

## 4. 核心接口设计

### 4.1 文件结构

```
railway_dispatch/qwen/
├── test_model.py              # [已存在] 模型测试
├── qwen_agent.py             # [新建] Qwen Agent实现
├── tool_registry.py          # [新建] Tools注册与管理
└── prompts.py                # [新建] Prompt模板
```

### 4.2 ToolRegistry类

```python
# tool_registry.py
from skills.dispatch_skills import (
    create_skills, execute_skill, DispatchSkillOutput
)
from solver.mip_scheduler import MIPScheduler

class ToolRegistry:
    """MCP Tools注册表 - 管理可用Skills"""

    def __init__(self, scheduler: MIPScheduler):
        self.scheduler = scheduler
        self.skills = create_skills(scheduler)

    def get_tools_schema(self) -> List[dict]:
        """获取Tools JSON Schema（用于Function Calling）"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "temporary_speed_limit_skill",
                    "description": "处理临时限速场景的列车调度...",
                    "parameters": {...}
                }
            },
            # ... other tools
        ]

    def execute(self, tool_name: str, arguments: dict) -> DispatchSkillOutput:
        """执行Tool - 调用MIP求解器"""
        return execute_skill(tool_name, self.skills, **arguments)
```

### 4.3 QwenAgent类

```python
# qwen_agent.py
from modelscope import AutoModelForCausalLM, AutoTokenizer

class QwenAgent:
    """基于Qwen模型的铁路调度Agent"""

    def __init__(self, model_path: str, scheduler: MIPScheduler):
        self.model = AutoModelForCausalLM.from_pretrained(...)
        self.tokenizer = AutoTokenizer.from_pretrained(...)
        self.tool_registry = ToolRegistry(scheduler)

    def analyze(self, delay_injection: Dict) -> AgentResult:
        """分析场景并执行调度"""
        # 1. 构建Prompt
        # 2. 调用Qwen推理
        # 3. 解析Tool Call
        # 4. 执行Skill（MIP求解）
        # 5. 返回结果
        pass
```

### 4.4 System Prompt设计

```
你是一个专业的铁路调度规划助手。

## 场景信息
{scenario_info}

## 可用工具（Skills）
{tools_description}

请分析场景，选择合适的工具执行调度优化。
```

## 5. Tool定义

### 5.1 temporary_speed_limit_skill

```json
{
    "name": "temporary_speed_limit_skill",
    "description": "处理临时限速场景的列车调度。适用于：铁路线路临时限速导致的多列列车延误调整",
    "parameters": {
        "type": "object",
        "properties": {
            "train_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "受影响列车ID列表"
            },
            "station_codes": {
                "type": "array", 
                "items": {"type": "string"},
                "description": "涉及的车站编码列表"
            },
            "delay_injection": {
                "type": "object",
                "description": "延误注入数据"
            },
            "optimization_objective": {
                "type": "string",
                "default": "min_max_delay",
                "enum": ["min_max_delay", "min_avg_delay"]
            }
        },
        "required": ["train_ids", "station_codes", "delay_injection"]
    }
}
```

### 5.2 sudden_failure_skill

```json
{
    "name": "sudden_failure_skill",
    "description": "处理突发故障场景的列车调度。适用于：列车设备故障、区间占用等单列车故障场景",
    "parameters": {...}
}
```

## 6. 实现步骤

### Task 1: 创建Prompt模板 (prompts.py)
- 场景分析Prompt
- 工具调用Prompt
- 结果总结Prompt

### Task 2: 创建Tool注册表 (tool_registry.py)
- Tools Schema定义
- 执行接口封装

### Task 3: 实现QwenAgent (qwen_agent.py)
- 模型加载
- 推理接口
- Tool Call解析

### Task 4: 测试与集成
- 临时限速场景测试
- 突发故障场景测试

## 7. 验收标准

1. **场景识别准确率**: >90%（与PlannerAgent规则引擎一致）
2. **Tool调用正确性**: 选择的Skill与场景类型匹配
3. **MIP求解**: 调度方案由纯数学整数规划生成
4. **执行成功率**: Skill执行成功并返回有效结果
