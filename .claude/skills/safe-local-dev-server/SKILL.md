---
name: safe-local-dev-server
description: Use before starting any ad-hoc dev server (npm run dev, uvicorn --reload, etc.) on a machine that also runs production/systemd-managed services for the same project. Checking for a port collision first prevents accidentally killing a live service.
---

## What went wrong once

An ad-hoc `npm run dev -p 3001` was started to test something locally, without checking whether port 3001 was already in use. It was — by `ledger-app-frontend.service`, the actual production frontend running under systemd. The new process either failed to bind or the port conflict resulted in the production service getting killed, and the real, in-use frontend went down (reported by the user as "手機連不上了" — phone can't connect).

## The check, before starting anything

```bash
systemctl --user list-units --all --type=service | grep -i <project-keyword>
ss -tln | grep <port>
```

If a systemd unit already owns the port you're about to use:
- **Don't start a second process on the same port.** Use a different port for the throwaway/test server (e.g. `-p 3002`), and confirm that port is free too.
- If you need to test against the production build itself, use the systemd service directly (`systemctl --user restart <service>`) rather than layering an ad-hoc process next to it.

## After you're done

Kill only the ad-hoc process you started (`pkill -f "next dev -p 3002"` or equivalent), and re-verify the production service is still healthy (`systemctl --user status <service>`, plus an actual `curl` against it) — don't assume it was untouched just because you used a different port for your own testing.
