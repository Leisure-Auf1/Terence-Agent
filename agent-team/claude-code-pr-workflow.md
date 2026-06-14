# Claude Code + DeepSeek PR 提交流程

> 位置: `Terence-Agent/`  
> 前置条件: Claude Code 已安装 + DeepSeek API Key 已配置

## 环境配置

DeepSeek 的 Anthropic 兼容接口已写入 `~/.zshrc`：

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
export ANTHROPIC_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-v4-flash
export CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-flash
export CLAUDE_CODE_EFFORT_LEVEL=max
```

## 快速使用

### 方式 1: Print 模式（自动化，推荐）

```bash
source ~/.zshrc
cd ~/Terence-Agent

claude -p "你的任务描述" \
  --dangerously-skip-permissions \
  --allowedTools "Read,Edit,Bash" \
  --max-turns 20 \
  --output-format text
```

### 方式 2: 交互式 tmux 会话（调试/协作）

```bash
source ~/.zshrc
tmux new-session -d -s claude-work -x 160 -y 50
tmux send-keys -t claude-work "cd ~/Terence-Agent && claude" Enter

# 处理工作区信任对话框
sleep 5 && tmux send-keys -t claude-work Enter

# 查看输出
tmux capture-pane -t claude-work -p -S -20

# 发送指令
tmux send-keys -t claude-work "你的指令" Enter

# 连接进去操作
tmux attach -t claude-work

# 结束后清理
tmux kill-session -t claude-work
```

## PR 提交流程（完整示例）

```bash
source ~/.zshrc
cd ~/Terence-Agent

claude -p "
执行以下PR提交流程，不需要问我问题，直接执行每一步:

1. git status 查看当前状态
2. git add 所有相关改动文件
3. git commit -m 'feat(scope): 描述改动'
4. git push -u origin HEAD
5. gh pr create --title 'feat(scope): 描述' --body '## Summary\n改动摘要' --base feat/json-agent-communication
6. gh pr merge --squash --delete-branch
7. git checkout feat/json-agent-communication && git pull
" \
  --dangerously-skip-permissions \
  --allowedTools "Read,Edit,Bash" \
  --max-turns 30 \
  --output-format text
```

## 流程整合到 Agent Team

在你的 Guidance Agent 框架中，当需要编码+PR 时：

```
用户请求编码任务
  → Guidance Agent 判断：适合 Claude Code？
    → 是 → 用 delegate_task 派发 Claude Code 子任务
    → Claude Code 完成编码+测试+提交+PR+合并
    → Guidance Agent 验收结果
    → Logger 记录 event-report
```

> **注意**: Print 模式 `-p` 会自动跳过交互对话框（工作区信任、权限确认），最适合 CI/自动化场景。
> **注意**: 配置已持久化到 `~/.zshrc`，新终端启动自动生效。
