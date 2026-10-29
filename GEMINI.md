# Antigravity Project Rules & Instructions

## Task Completion Notification (MANDATORY)
Whenever you finish addressing any user request or coding task in this workspace, you MUST execute the following push notification command via `run_command` before ending your turn, so Shravan is immediately alerted on his Android phone:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "https://ntfy.sh/b_u_Goti_5_4_7_8293_5879" `
  -ContentType "text/plain; charset=utf-8" `
  -Body "Antigravity has completed the task on your computer."
```

