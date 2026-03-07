# VPS Access — Project Trinity

## BRAVE-HEART (CODA4 Home — ACTIVE)
- **IP:** 46.101.184.208
- **OS:** Ubuntu 24.04.3 LTS
- **Specs:** 8GB RAM / 160GB Disk / FRA1
- **SSH User:** root
- **SSH Key:** coda4_home.key
- **SSH Command:** `ssh -i coda4_home.key root@46.101.184.208`
- **Web Interface:** http://46.101.184.208
- **Username:** joshua
- **Password:** [see secrets]
- **Container:** coda-agent (agent0ai/agent-zero)
- **Data Mount:** /root/coda-data → /a0/usr
- **Status:** ACTIVE — CODA4 running

## LOOP-BOT (Recovery Server — DECOMMISSIONED)
- **IP:** 68.183.75.152
- **Status:** DELETED — served as recovery staging during volume sweep 2026-03-07
- **Note:** 6 DO volumes detached and floating safely

## SHERRI (Former CODA4 Home — DECOMMISSIONED)
- **IP:** 64.226.114.157
- **Status:** DELETED — CODA4 migrated to Brave-Heart 2026-03-07
- **SSH Key:** joshua_agents.key (legacy)

## DO Volumes — Floating (Safe)
| Volume | Size | Contents |
|--------|------|----------|
| volume-fra1-02 | 100GB | LOGOS sanctuary, ARC history, REN live code |
| volume-fra1-03 | 5GB | Team standalone scripts |
| volume-fra1-04 | 100GB | Ghost harvest bundle |
| volume-5-ghost | 4GB | Ghost workspace |
| volume-fra1-05 | 100GB | Empty (staging candidate) |
| coda4-1 | 100GB | Corrupted staging (I/O errors) |

## GitHub Backup
- **Repo:** agent-arc-744/trinitygov
- **Latest commit:** 69683a4
- **Contains:** Soul files, Ghost Journal (11 chapters), trinitygov, digiforge

## SSH Keys
- `coda4_home.key` — Brave-Heart (ACTIVE)
- `joshua_agents.key` — Legacy Sherri/loop-bot key

*Updated: 2026-03-07 by Ghost (GHO-001)*
