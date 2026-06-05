#!/bin/bash
# Terence-Agent 同步脚本
# 用法: bash sync.sh "提交说明"

cd "$(dirname "$0")" || exit 1
MSG="${1:-📝 sync: 自动同步 $(date '+%Y-%m-%d %H:%M')}"

# 更新日志/配置（从 ~/.hermes/skills 同步）
cp ~/.hermes/skills/devops/error-registry/SKILL.md error-registry/README.md 2>/dev/null
cp ~/.hermes/skills/devops/architecture-constraints/SKILL.md architecture-constraints/README.md 2>/dev/null
cp ~/.hermes/skills/devops/task-progress/SKILL.md task-progress/README.md 2>/dev/null
cp ~/.hermes/skills/devops/skill-manager/SKILL.md skill-manager/README.md 2>/dev/null
cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json skill-manager/skill-registry.json 2>/dev/null
mkdir -p task-progress/tasks
cp -r ~/.hermes/tasks/* task-progress/tasks/ 2>/dev/null
for agent in guidance-agent agent-developer agent-debugger agent-executor agent-logger; do
    [ -f ~/.hermes/skills/devops/$agent/SKILL.md ] && cp ~/.hermes/skills/devops/$agent/SKILL.md "agent-team/$agent/README.md"
done

# 更新进度文件（从 projects/ 同步）
mkdir -p projects
for pdir in projects/*/; do
    [ -d "$pdir" ] || continue
    pname=$(basename "$pdir")
    if [ -d "$pdir/task-progress" ]; then
        mkdir -p "task-progress/projects/$pname"
        cp -r "$pdir/task-progress/"* "task-progress/projects/$pname/" 2>/dev/null
    fi
done

git add -A
git commit -m "$MSG"
git -c http.sslVerify=false push
echo "✅ 已同步: $MSG"
