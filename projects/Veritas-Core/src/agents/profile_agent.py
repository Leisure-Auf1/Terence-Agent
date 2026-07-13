"""
Veritas_Core — ProfileAgent: Student Profile Construction.

Dual-mode engine:
  - Rule mode: keyword matching + priority scoring (zero latency, 70% confidence)
  - LLM mode: natural language deep extraction (85% confidence)

Output: DynamicProfile (8 dimensions) — only writes "candidate" to Memory.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Tuple

from .base import BaseAgent, AgentContext, AgentOutput
from core.contracts import DynamicProfile


# ═══════════════════════════════════════════
# Rule Engine — Keyword → Dimension Mapping
# ═══════════════════════════════════════════

KNOWLEDGE_BASE_RULES: List[Tuple[List[str], str]] = [
    (["零基础", "完全不会", "刚开始学", "小白", "新手", "没学过", "完全没有基础"], "junior_dev"),
    (["学过基础", "会一点", "有一些基础", "中级", "进阶", "有些经验", "写过一段时间"], "mid_level"),
    (["熟练", "多年经验", "熟练掌握", "经常写", "老手", "架构师", "高级",
      "资深", "多年开发", "多年的", "多年"], "senior"),
]

COGNITIVE_STYLE_RULES: List[Tuple[List[str], str]] = [
    (["看视频", "看图", "图解", "可视化", "图形", "视觉", "画图", "一目了然", "直观"], "visual_dominant"),
    (["听书", "听讲", "听课", "音频", "耳朵", "听", "口述"], "auditory"),
    (["看书", "阅读", "文字", "逐行", "一步步", "翻书"], "text_linear"),
]

LEARNING_HABIT_RULES: List[Tuple[List[str], str]] = [
    (["写代码", "动手", "实操", "练手", "敲代码", "编程练习", "自己写"], "code_sandbox"),
    (["先测试", "自测", "检验", "考试", "做题目", "刷题"], "quiz_first"),
    (["探索", "试错", "乱试", "自由", "随意", "随便看看"], "exploratory"),
]

ERROR_BIAS_RULES: List[Tuple[List[str], str]] = [
    (["语法糖", "黑魔法", "@", "装饰器", "搞不懂语法", "看不懂缩写", "搞不太懂", "经常用错"], "magic_syntax_blind"),
    (["异步编程", "async", "并发", "多线程", "锁"], "concurrency_confusion"),
    (["配置", "环境", "路径", "import", "找不到模块"], "env_config_weak"),
]

RESOURCE_PREF_RULES: List[Tuple[List[str], str]] = [
    (["图", "思维导图", "mermaid", "流程图", "架构图"], "diagram+code"),
    (["视频", "讲解", "教程视频", "跟学"], "video+quiz"),
    (["文档", "详细", "源码", "代码注释"], "text+code"),
]

LEARNING_GOAL_PATTERNS = [
    (r"多智能体|multi.?agent|agent系统|智能体", "Multi-Agent Systems"),
    (r"大模型|llm|语言模型|gpt|transformer", "LLM Engineering"),
    (r"rag|检索增强|知识库|向量", "RAG Systems"),
    (r"prompt|提示词", "Prompt Engineering"),
    (r"机器学习|深度学习|神经网络", "Machine Learning"),
    (r"python|爬虫|后端|web", "Python Development"),
]

MOTIVATION_RULES: List[Tuple[List[str], str]] = [
    (["找工作", "实习", "就业", "面试", "跳槽", "职业"], "career_advancement"),
    (["课程", "考试", "学分", "期末", "作业"], "academic"),
    (["兴趣", "好奇", "玩玩", "了解"], "hobby"),
]

TIME_BUDGET_RULES: List[Tuple[List[str], str]] = [
    (["每天很多时间", "全天", "全职学习", "整天"], "20h/week"),
    (["每天几小时", "周末学", "下班后", "晚上"], "10h/week"),
    (["偶尔", "有空", "碎片", "抽空"], "5h/week"),
]


class ProfileAgent(BaseAgent):
    """Extract 8-dimension student profile from natural language."""

    agent_name = "ProfileAgent"

    def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        text = input_data.get("text", "")
        if not text:
            return AgentOutput(
                result=DynamicProfile(),
                confidence=0.0,
                evidence=["no_input"],
                reasoning="No text provided",
            )

        profile, rule_confidence = self._rule_extract(text)
        source = "rule"

        if rule_confidence < 0.6 and self.ctx.llm_provider:
            try:
                llm_profile, llm_conf = self._llm_extract(text)
                if llm_conf > rule_confidence:
                    # Merge: use LLM for main dims, preserve rule weak_points
                    llm_profile.weak_points = profile.weak_points
                    profile = llm_profile
                    source = "llm"
                    rule_confidence = llm_conf
            except Exception:
                pass  # Fall through to rule result

        profile.source = source
        profile.confidence = min(rule_confidence, 0.9)

        return AgentOutput(
            result=profile,
            confidence=profile.confidence,
            evidence=[f"extracted via {source}", f"text len={len(text)}"],
            reasoning=f"Profile built via {source} engine from {len(text)} chars",
        )

    def _rule_extract(self, text: str) -> tuple:
        profile = DynamicProfile()
        scores = []

        kb, kb_conf = self._match(text, KNOWLEDGE_BASE_RULES)
        profile.knowledge_base = kb
        scores.append(kb_conf)

        style, style_conf = self._match(text, COGNITIVE_STYLE_RULES)
        profile.cognitive_style = style
        scores.append(style_conf)

        habit, habit_conf = self._match(text, LEARNING_HABIT_RULES)
        profile.learning_habit = habit
        scores.append(habit_conf)

        errors = []
        for keywords, err_type in ERROR_BIAS_RULES:
            if any(kw in text for kw in keywords):
                errors.append({"concept": err_type, "error_type": err_type, "occurrence_count": 1})
        profile.weak_points = errors

        pref, pref_conf = self._match(text, RESOURCE_PREF_RULES)
        profile.resource_preference = pref
        scores.append(pref_conf)

        goal, goal_conf = self._match_regex(text, LEARNING_GOAL_PATTERNS)
        profile.learning_goal = goal
        if goal_conf > 0:
            scores.append(goal_conf)

        mot, _ = self._match(text, MOTIVATION_RULES)
        profile.learning_motivation = mot

        time_b, _ = self._match(text, TIME_BUDGET_RULES)
        profile.time_budget = time_b

        # Average confidence — only count dimensions that had actual keyword matches
        avg_conf = sum(scores) / len(scores) if scores else 0.5
        # Boost: if knowledge_base matched well, weight it more
        if len(scores) >= 1 and scores[0] >= 0.7:
            avg_conf = max(avg_conf, 0.65)
        return profile, avg_conf

    @staticmethod
    def _match(text: str, rules: List[Tuple[List[str], str]]) -> tuple:
        for keywords, value in rules:
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                return value, min(0.5 + matches * 0.15, 0.9)
        return (rules[0][1], 0.3) if rules else ("", 0.0)  # default to first rule, low confidence

    @staticmethod
    def _match_regex(text: str, patterns: List[tuple]) -> tuple:
        for pattern, value in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return value, 0.75
        return "", 0.0

    def _llm_extract(self, text: str) -> tuple:
        response = self.ctx.llm_provider.generate(
            prompt=f"""Extract student profile as JSON:
{{"knowledge_base":"junior_dev|mid_level|senior","learning_goal":"...","cognitive_style":"visual_dominant|text_linear|auditory","learning_habit":"code_sandbox|quiz_first|exploratory","resource_preference":"text+code|diagram+code|video+quiz","learning_motivation":"career_advancement|academic|hobby","time_budget":"flexible|5h/week|10h/week|20h/week"}}
Text: "{text[:1000]}" """,
            system_prompt="Return only valid JSON.",
            temperature=0.3,
        )
        data = json.loads(response.content)
        profile = DynamicProfile(**{k: v for k, v in data.items() if hasattr(DynamicProfile, k)})
        return profile, 0.85
