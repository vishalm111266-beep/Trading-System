# GitHub Advanced Setup Guide

## Step 2: Branch Protection Rules
1. Go to: https://github.com/vishalm111266-beep/Trading-System/settings/branches
2. Click **"Add branch protection rule"**
3. In "Branch name pattern", type: `main`
4. Check these options:
   - ☑ **Require a pull request before merging**
     - ☑ Require approvals (1)
   - ☑ **Require status checks to pass before merging**
     - ☑ Require branches to be up to date
     - Search and select the CI workflow checks
   - ☑ **Do not allow bypassing the above settings**
5. Click **"Create"**

## Step 5: GitHub Projects (Kanban Board)
1. Go to: https://github.com/vishalm111266-beep/Trading-System/projects
2. Click **"Link a project"** → **"Create new project"**
3. Select **"Board"** template
4. Name: `Trading System Development`
5. Add columns: `Backlog` → `In Progress` → `Review` → `Done`
6. Start adding issues as cards

## Step 6: Code Security & Analysis
1. Go to: https://github.com/vishalm111266-beep/Trading-System/settings/security_analysis
2. Enable:
   - ☑ **Dependabot alerts** (already configured via dependabot.yml)
   - ☑ **Dependabot security updates**
   - ☑ **Code scanning** → Click "Set up" → Select "CodeQL" → "Default"
   - ☑ **Secret scanning**
3. Click **"Enable"** for each

## After Setup
- Push all changes: `git push origin main`
- CI will run automatically on every push
- Dependabot will check for updates every Monday
- Issues/PRs will use the templates
