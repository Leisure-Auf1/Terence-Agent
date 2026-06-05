#!/bin/bash
# Terence-Agent 同步脚本
# 用法: bash sync.sh "提交说明"

cd "$(dirname "$0")" || exit 1
MSG="${1:-📝 sync: 自动同步 $(date '+%Y-%m-%d %H:%M')}"

# 更新内容
cp ~/.hermes/skills/devops/error-registry/SKILL.md error-registry/README.md
cp ~/.hermes/skills/devops/architecture-constraints/SKILL.md architecture-constraints/README.md
cp ~/.hermes/skills/devops/task-progress/SKILL.md task-progress/README.md
cp ~/.hermes/skills/devops/skill-manager/SKILL.md skill-manager/README.md
cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json skill-manager/skill-registry.json
mkdir -p task-progress/tasks
cp -r ~/.hermes/tasks/* task-progress/tasks/ 2>/dev/null
for agent in guidance-agent agent-developer agent-debugger agent-executor agent-logger; do
    [ -f ~/.hermes/skills/devops/$agent/SKILL.md ] && cp ~/.hermes/skills/devops/$agent/SKILL.md "agent-team/$agent/README.md"
done

git add -A
git commit -m "$MSG"
git -c http.sslVerify=false push
echo "✅ 已同步: $MSG"
