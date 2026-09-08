---
name: cloud-sync-branch
description: 云端修改文件同步专用分支，自动与远程同步
metadata:
  type: project
  user: lucas
  project: AgentSoftware
  reference: https://github.com/Lucasss1916/AgentSoftware
---

# Cloud Sync Branch

专用分支用于**云端修改文件**的同步测试和自动化同步。

## 工作流程

### 1. 云端修改文件
- 在 GitHub Web 界面直接编辑文件
- 或通过 GitHub Codespaces / GitHub.dev 直接在云端编辑

### 2. 提交到远程
**必须 push 到 `origin/cloud-sync-main` 分支**（推荐）

```bash
git push origin cloud-sync-main
```

### 3. 本地自动同步
```bash
git pull --rebase
```

## 当前状态

- 分支: `cloud-sync-main`
- 远程: `origin/cloud-sync-main`
- 最后同步: `8c61cd5` (本地推送的 commit)

## 注意事项

- **冲突处理**: 云端修改的文件如果与本地修改冲突，会导致合并失败
- **最佳实践**: 
  1. 云端修改前，先 `git pull --rebase`
  2. 云端提交后，本地再 `git pull --rebase`
  3. 建议使用 `git rebase` 而非 `git merge`

## 命令速查

```bash
# 创建并切换到云端同步分支
git checkout -b cloud-sync-main

# 推送云端修改
git push origin cloud-sync-main

# 本地同步
git pull --rebase
```

**推荐使用场景**: 
- 在 GitHub Web 直接编辑 README.md / 配置文件
- 使用 GitHub Codespaces 远程开发
- 多人协作时云端修改主要文件