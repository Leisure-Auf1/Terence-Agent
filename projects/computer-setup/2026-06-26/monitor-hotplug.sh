#!/bin/bash
# 显示器热插拔处理脚本 — niri 下自动切换外接/笔记本屏
# 外接显示器连接时 → 关闭笔记本屏 (eDP-1)
# 外接显示器断开时 → 打开笔记本屏 (eDP-1)
#
# 日志: logger -t monitor-hotplug "message"
# 安装: sudo cp this /usr/local/bin/ && chmod +x

USER="Terence"
USER_ID="1000"

# ---- 自动发现外接 DP/HDMI 显示器 ----
EXTERNAL_STATUS=""
EXTERNAL_NAME=""
for card in /sys/class/drm/card*-[DH]*; do
    name=$(basename "$card")
    status=$(cat "$card/status" 2>/dev/null)
    # 排除 laptop 内置屏 (eDP)
    if [ "$status" = "connected" ] && echo "$name" | grep -qv "eDP"; then
        EXTERNAL_STATUS="connected"
        EXTERNAL_NAME="$name"
        break
    fi
done

# 没有外接显示器
if [ -z "$EXTERNAL_STATUS" ]; then
    EXTERNAL_STATUS="disconnected"
fi

# ---- 找到 niri socket ----
NIRI_SOCKET=$(ls /run/user/$USER_ID/niri.*.sock 2>/dev/null | head -1)
if [ -z "$NIRI_SOCKET" ]; then
    logger -t monitor-hotplug "niri socket not found, skipping"
    exit 0
fi

run_niri() {
    sudo -u "$USER" env NIRI_SOCKET="$NIRI_SOCKET" niri msg "$@"
}

# ---- 检查 eDP-1 当前状态（从文本输出检测） ----
LAPTOP_OUTPUT=$(run_niri outputs 2>/dev/null | grep -A3 "(eDP-1)")
if echo "$LAPTOP_OUTPUT" | grep -q "Current mode"; then
    LAPTOP_IS_ON="true"
elif echo "$LAPTOP_OUTPUT" | grep -q "Disabled"; then
    LAPTOP_IS_ON="false"
else
    LAPTOP_IS_ON="unknown"
fi

# ---- 执行切换 ----
if [ "$EXTERNAL_STATUS" = "connected" ]; then
    if [ "$LAPTOP_IS_ON" = "true" ]; then
        logger -t monitor-hotplug "External connected ($EXTERNAL_NAME), turning laptop OFF"
        run_niri output "DP-3" on 2>/dev/null
        sleep 0.3
        run_niri output "eDP-1" off 2>/dev/null
        logger -t monitor-hotplug "Laptop OFF, external ON"
    else
        logger -t monitor-hotplug "External connected ($EXTERNAL_NAME), already correct, skip"
    fi
else
    if [ "$LAPTOP_IS_ON" = "false" ]; then
        logger -t monitor-hotplug "External disconnected, turning laptop ON"
        run_niri output "eDP-1" on 2>/dev/null
        logger -t monitor-hotplug "Laptop ON"
    else
        logger -t monitor-hotplug "External disconnected, already correct, skip"
    fi
fi
