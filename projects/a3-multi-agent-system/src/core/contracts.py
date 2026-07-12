"""
Phase 4 — 元学习进化拓扑: 结构化记忆契约
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class FailurePatternLesson:
    error_type: str
    problem_context: str
    root_cause_analysis: str
    anti_pattern_code: str
    golden_patch_code: str
    abstract_lint_rule: str
    node_id: str = ""
    severity: str = "HIGH"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type, "problem_context": self.problem_context,
            "root_cause_analysis": self.root_cause_analysis,
            "anti_pattern_code": self.anti_pattern_code,
            "golden_patch_code": self.golden_patch_code,
            "abstract_lint_rule": self.abstract_lint_rule,
            "node_id": self.node_id, "severity": self.severity,
            "created_at": self.created_at, "tags": self.tags,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailurePatternLesson":
        return cls(
            error_type=data["error_type"], problem_context=data["problem_context"],
            root_cause_analysis=data["root_cause_analysis"],
            anti_pattern_code=data["anti_pattern_code"],
            golden_patch_code=data["golden_patch_code"],
            abstract_lint_rule=data["abstract_lint_rule"],
            node_id=data.get("node_id", ""), severity=data.get("severity", "HIGH"),
            created_at=data.get("created_at", ""), tags=data.get("tags", []),
        )

    @classmethod
    def from_json(cls, raw: str) -> "FailurePatternLesson":
        return cls.from_dict(json.loads(raw))

    def semantic_anchor(self) -> str:
        return f"Error: {self.error_type}. Context: {self.problem_context}. Rule: {self.abstract_lint_rule}"


BUILTIN_LESSONS: List[FailurePatternLesson] = [
    FailurePatternLesson(
        error_type="CognitiveOverload",
        problem_context="Node 1: 单节塞入10个概念(闭包/高阶/装饰器/语法糖/一等公民/functools/wraps/nonlocal/作用域/装饰器工厂)",
        root_cause_analysis="大模型的知识诅咒——低估初学者认知上限(3个)。",
        anti_pattern_code="# 整节堆入全部10个概念\n## 1. 全部概念\n- 闭包\n- 高阶函数\n- ...",
        golden_patch_code="## §1.1 函数是对象(3概念)\n## §1.2 闭包(3概念)\n## §1.3 装饰器(4概念)",
        abstract_lint_rule="每节新概念 ≤ 3 个, 用比喻而非定义引入",
        node_id="node-1", severity="CRITICAL", tags=["cognitive-load", "curse-of-knowledge"],
    ),
    FailurePatternLesson(
        error_type="TypeAnnotationMissing",
        problem_context="Node 2 AST Gate拒绝: solution.py类型注解覆盖率0%",
        root_cause_analysis="大模型生成代码倾向省略类型注解——训练数据中大量无类型提示示例。",
        anti_pattern_code="def retry(max_tries=3, delay=1):\n    def decorator(func): ...",
        golden_patch_code="def retry(max_tries:int=3, delay:float=1)->Callable:\n    def decorator(func:Callable)->Callable: ...",
        abstract_lint_rule="生成函数必须包含完整类型注解, 覆盖率 ≥ 50%",
        node_id="node-2", severity="HIGH", tags=["type-hints"],
    ),
    FailurePatternLesson(
        error_type="ProbeDetectionFalseNegative",
        problem_context="Node 1 测试: get_logger()在空壳函数时返回None触发AttributeError",
        root_cause_analysis="空壳函数(def logger:pass)返回None, 但名字检查通过导致装饰器返回None。",
        anti_pattern_code="if logger_func.__name__ != 'logger': ...\nreturn logger_func  # 空壳有名字但无实现!",
        golden_patch_code="try:\n  @logger_func\n  def _probe():return 42\n  if _probe()==42: return logger_func\nexcept: pass\nreturn test_solution_logger()",
        abstract_lint_rule="学生代码加载器必须用probe检测实际装饰验证, 不能仅检查函数名",
        node_id="node-1", severity="HIGH", tags=["test-design", "probe"],
    ),
    FailurePatternLesson(
        error_type="BackwardValidationBypass",
        problem_context="Node 2 Gate反向验证: pass stubs通过测试(测试文件内置probe自动兜底)",
        root_cause_analysis="Probe机制与Gate反向验证存在设计冲突——智能fallback绕过骨架必须失败的约束。",
        anti_pattern_code="# Gate直接运行含probe的原始测试文件\nsubprocess.run(['pytest','test_case.py'])",
        golden_patch_code="# Gate用剥壳测试(无fallback)\nstripped_test='from exercise import retry\\ndef test():...'\nsubprocess.run(['pytest',tmp_test])",
        abstract_lint_rule="Gate反向验证必须用无fallback的剥壳测试",
        node_id="node-2", severity="HIGH", tags=["review-gate", "backward"],
    ),
    FailurePatternLesson(
        error_type="PropertySetterExtractorGap",
        problem_context="Node 3 UserSim误报: 讲义已教.setter但分析器认为'property setter'未教",
        root_cause_analysis="概念提取器基于字符串精确匹配, 无法识别'property setter'等价于代码模式'.setter'。",
        anti_pattern_code="if 'property setter' not in taught_concepts:\n    gaps.append('property setter')",
        golden_patch_code="code_patterns={'property setter':r'\\.setter'}\nif re.search(code_patterns['property setter'],lecture_text):\n    taught_concepts.append('property setter')",
        abstract_lint_rule="概念匹配需检查名称+等价代码模式+上下文别名",
        node_id="node-3", severity="MEDIUM", tags=["extractor", "alias"],
    ),
]
