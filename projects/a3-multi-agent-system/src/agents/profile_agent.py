"""
Phase 5.1 — ProfileAgent: 学生自然语言 → DynamicProfile

双模式:
  规则模式 — 关键词匹配 + 优先级推理 (零延迟, 可解释)
  LLM 扩展模式 — 调用大模型进行细粒度语义提取

输出: DynamicProfile (兼容 agent_router.py 的六维画像合约)
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProfileExtractionResult:
    """ProfileAgent 提取结果"""
    profile: "DynamicProfile"  # noqa: F821
    source: str = "rule"       # rule | llm
    confidence: float = 1.0    # 提取置信度 (0-1)
    raw_keywords: List[str] = field(default_factory=list)
    llm_reasoning: str = ""    # LLM 模式下的推理过程

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "source": self.source,
            "confidence": self.confidence,
            "raw_keywords": self.raw_keywords,
        }


# ──────────────────────────────────────────────
# 规则引擎 — 关键词 → 维度映射表
# ──────────────────────────────────────────────

# 知识基础映射
KNOWLEDGE_BASE_RULES: List[Tuple[List[str], str]] = [
    (["零基础", "完全不会", "刚开始学", "没有任何编程经验", "小白", "新手",
      "没学过", "完全没"], "junior_dev"),
    (["学过基础", "会一点", "学过一些", "有一定的", "有一些", "有基础",
      "写过一段时间", "中级", "进阶", "有些经验"], "mid_level"),
    (["熟练", "多年经验", "熟练掌握", "经常写", "老手", "架构师", "高级",
      "资深", "多年开发"], "senior"),
]

# 认知风格映射
COGNITIVE_STYLE_RULES: List[Tuple[List[str], str]] = [
    (["看视频", "看图", "图解", "可视化", "图形", "视觉", "画图", "一目了然", "直观"], "visual_dominant"),
    (["听书", "听讲", "听课", "音频", "耳朵", "听", "口述"], "auditory"),
    (["看书", "阅读", "文字", "逐行", "一步步", "翻书"], "text_linear"),
]

# 常见错误倾向
ERROR_BIAS_RULES: List[Tuple[List[str], str]] = [
    (["语法糖", "黑魔法", "@", "装饰器", "搞不懂语法", "看不懂缩写"], "magic_syntax_blind"),
    (["缩进", "缩进老是错", "冒号", "格式"], "indentation_errors"),
    (["变量", "作用域", "命名", "找不到变量", "undefined"], "variable_scoping"),
    (["类型", "int", "str", "类型报错", "type error"], "type_mismatch"),
    (["导入", "import", "找不到模块", "模块"], "import_issues"),
]

# 学习节奏映射
LEARNING_PACE_RULES: List[Tuple[List[str], str]] = [
    (["急着用", "快速上手", "来不及", "赶时间", "考试", "面试", "马上", "快速", "快点"], "fast_track"),
    (["慢慢来", "仔细", "彻底", "深挖", "追根究底", "搞懂本质", "底层", "深入"], "deep_dive"),
    # normal 是默认值
]

# 交互偏好映射
INTERACTION_RULES: List[Tuple[List[str], str]] = [
    (["动手", "写代码", "敲代码", "调试", "运行", "沙箱", "实操", "练习", "自己写"], "code_sandbox"),
    (["做题", "测试", "选择题", "考试", "题目", "测验"], "quiz_first"),
    (["先看", "先读", "先理解", "浏览", "翻阅", "翻翻"], "passive_read"),
]

# 挫败阈值映射
FRUSTRATION_RULES: List[Tuple[List[str], str]] = [
    (["容易放弃", "挫败", "没信心", "鼓励", "耐心", "安慰", "温柔", "害怕", "不敢", "总错"], "low"),
    (["不怕", "无所谓", "抗压", "皮实", "随便", "尽管来"], "high"),
    # medium 是默认值
]


# ──────────────────────────────────────────────
# ProfileAgent
# ──────────────────────────────────────────────

class ProfileAgent:
    """
    学生画像提取 Agent.

    输入: 自然语言学生描述
    输出: DynamicProfile (六维画像)

    两种模式:
      1. extract(text) — 纯规则模式 (零延迟, 可解释)
      2. extract_with_llm(text, router) — LLM 增强模式
    """

    # 模式默认值
    DEFAULTS = {
        "knowledge_base": "junior_dev",
        "cognitive_style": "visual_dominant",
        "error_prone_bias": "magic_syntax_blind",
        "learning_pace": "normal",
        "interaction_preference": "code_sandbox",
        "frustration_threshold": "medium",
    }

    def __init__(self, default_overrides: Optional[Dict[str, str]] = None):
        self.defaults = {**self.DEFAULTS, **(default_overrides or {})}

    # ── 规则模式 ──────────────────────────────

    def extract(self, text: str) -> ProfileExtractionResult:
        """
        基于规则的画像提取.

        Args:
            text: 学生自然语言描述

        Returns:
            ProfileExtractionResult (source="rule")
        """
        from core.agent_router import DynamicProfile

        keywords = self._tokenize(text)
        raw_keywords = keywords.copy()

        profile = DynamicProfile(
            knowledge_base=self._match_rule(keywords, KNOWLEDGE_BASE_RULES,
                                            self.defaults["knowledge_base"]),
            cognitive_style=self._match_rule(keywords, COGNITIVE_STYLE_RULES,
                                              self.defaults["cognitive_style"]),
            error_prone_bias=self._match_rule(keywords, ERROR_BIAS_RULES,
                                               self.defaults["error_prone_bias"]),
            learning_pace=self._match_rule(keywords, LEARNING_PACE_RULES,
                                            self.defaults["learning_pace"]),
            interaction_preference=self._match_rule(keywords, INTERACTION_RULES,
                                                     self.defaults["interaction_preference"]),
            frustration_threshold=self._match_rule(keywords, FRUSTRATION_RULES,
                                                     self.defaults["frustration_threshold"]),
        )

        # 计算置信度 — 匹配到的维度越多越高
        non_default = sum(
            1 for k, v in profile.to_dict().items()
            if v != self.defaults.get(k)
        )
        confidence = min(non_default / 3, 1.0)

        return ProfileExtractionResult(
            profile=profile,
            source="rule",
            confidence=confidence,
            raw_keywords=raw_keywords,
        )

    # ── LLM 扩展模式 ──────────────────────────

    LLM_PROMPT_TEMPLATE = """你是一个学生画像分析专家。请根据学生的自然语言描述，提取六维学习画像。

学生描述: {student_text}

请输出 JSON，包含以下字段 (必须从候选值中选择):

{{
  "knowledge_base": "junior_dev | mid_level | senior",
  "cognitive_style": "visual_dominant | text_linear | auditory",
  "error_prone_bias": "magic_syntax_blind | indentation_errors | variable_scoping | type_mismatch | import_issues",
  "learning_pace": "fast_track | normal | deep_dive",
  "interaction_preference": "code_sandbox | quiz_first | passive_read",
  "frustration_threshold": "low | medium | high",
  "reasoning": "一句话推理总结"
}}

只输出 JSON，不要任何额外文本。"""

    def extract_with_llm(
        self,
        text: str,
        router: Any = None,
    ) -> ProfileExtractionResult:
        """
        LLM 增强的画像提取.

        Args:
            text: 学生自然语言描述
            router: AgentRouter 实例 (用于 LLM 调用)

        Returns:
            ProfileExtractionResult (source="llm")
        """
        from core.agent_router import DynamicProfile

        if router is None:
            # 无 router 时回退到规则模式
            return self.extract(text)

        prompt = self.LLM_PROMPT_TEMPLATE.format(student_text=text)

        payload = {
            "model": "deepseek-v4-pro",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        }

        try:
            response = router.route_request("ProfileAgent", payload)
            content = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "{}")
            )
            data = json.loads(content)
        except Exception:
            # LLM 失败 → 规则兜底
            return self.extract(text)

        reasoning = data.pop("reasoning", "")

        # 验证候选值
        allowed = {
            "knowledge_base": {"junior_dev", "mid_level", "senior"},
            "cognitive_style": {"visual_dominant", "text_linear", "auditory"},
            "error_prone_bias": {
                "magic_syntax_blind", "indentation_errors",
                "variable_scoping", "type_mismatch", "import_issues",
            },
            "learning_pace": {"fast_track", "normal", "deep_dive"},
            "interaction_preference": {"code_sandbox", "quiz_first", "passive_read"},
            "frustration_threshold": {"low", "medium", "high"},
        }

        sanitized = {}
        for key, valid_set in allowed.items():
            value = data.get(key, self.defaults[key])
            sanitized[key] = value if value in valid_set else self.defaults[key]

        profile = DynamicProfile(**sanitized)

        return ProfileExtractionResult(
            profile=profile,
            source="llm",
            confidence=0.9,
            llm_reasoning=reasoning,
        )

    # ── 辅助方法 ──────────────────────────────

    def _tokenize(self, text: str) -> List[str]:
        """分词: 全文 + 按常见分隔符切分短语"""
        tokens = [text]  # 全文匹配用于连续短语
        # 按标点切分短语
        for part in re.split(r"[，。,\.!！?？、\s]+", text):
            part = part.strip()
            if part:
                tokens.append(part)
        return tokens

    def _match_rule(
        self,
        tokens: List[str],
        rules: List[Tuple[List[str], str]],
        default: str,
    ) -> str:
        """
        规则匹配: 按优先级返回第一个命中的值.

        每条规则是一组关键词 → 维度值.
        全文匹配任意关键词即命中.
        """
        for keywords, value in rules:
            for token in tokens:
                for kw in keywords:
                    if kw in token:
                        return value
        return default

    def get_prompt_hint(self, result: ProfileExtractionResult) -> str:
        """根据提取结果生成 Prompt 提示注入文本"""
        return result.profile.to_system_prompt_hint()
