# 🚀 Promethean Light - Project Launcher

**Launch multiple projects in Windows Terminal with Claude Code ready to go!**

---

## ✨ Features

- 📁 **Auto-discovers projects** from `C:\Code\projects`
- ☑️ **Interactive checkbox UI** - select multiple projects with arrow keys + spacebar
- 🖥️ **Windows Terminal tabs** - each project opens in its own tab
- 🤖 **Claude Code ready** - `claude` command auto-runs in each tab
- 🎯 **Seamless workflow** - start coding immediately

---

## 🎮 How to Use

### Option 1: Complete Workflow (Recommended)
**Double-click: `START_WITH_PROJECTS.bat`**

You'll see a menu:
```
[1] Start Daemon + Launch Projects  ← Choose this!
[2] Launch Projects Only (daemon already running)
[3] Start Daemon Only (no projects)
```

Choose **[1]** to:
1. Start Promethean Light daemon in background
2. Show project selection UI
3. Launch selected projects in Windows Terminal tabs

### Option 2: Projects Only
**Double-click: `LAUNCH_PROJECTS.bat`**

Just launches the project selector without starting the daemon (useful if daemon is already running).

---

## 📋 Interactive Selection UI

When the launcher starts, you'll see:

```
==============================================================
  PROMETHEAN LIGHT - PROJECT LAUNCHER
==============================================================

  Select projects to open in Claude Code
  • Use ↑↓ to navigate
  • Space to select/deselect
  • Enter to launch

==============================================================

Found 14 project(s):

? Select projects to open (Space to select, Enter to confirm)
  ○ business-tools
  ○ Capability Matrix
  ○ client-projects
❯ ○ Contacts
  ○ Files and Folder Convention
  ○ hr-recruitment
  ○ internal-tools
  ○ Pod Structure
  ○ project-sentinel
  ○ RUGS
  ○ Sales
  ○ training-gamification
```

**Controls:**
- **↑↓** - Navigate up/down
- **Space** - Toggle selection (○ → ◉)
- **Enter** - Launch selected projects
- **Ctrl+C** - Cancel

---

## 🎯 What Happens After Selection

If you select `project-sentinel`, `hr-recruitment`, and `Pod Structure`, the launcher will:

1. Open Windows Terminal with 4 tabs:
   - **Tab 1**: Promethean Light (`C:\Code\Promethian  Light`) with Claude ready
   - **Tab 2**: 📁 project-sentinel with Claude ready
   - **Tab 3**: 📁 hr-recruitment with Claude ready
   - **Tab 4**: 📁 Pod Structure with Claude ready

2. Each tab automatically runs:
   ```bash
   cd "C:\Code\projects\{project-name}"
   claude
   ```

3. You can immediately start coding!

---

## 🛠️ Requirements

- **Windows Terminal** - [Install here](https://aka.ms/terminal) if not already installed
- **inquirer** - Auto-installed when running for the first time
- **Claude Code CLI** - Must be in your PATH

---

## 📂 File Overview

| File | Purpose |
|------|---------|
| `project_launcher.py` | Core Python script - scans projects, shows UI, launches tabs |
| `LAUNCH_PROJECTS.bat` | Quick launcher - projects only |
| `START_WITH_PROJECTS.bat` | Full workflow - daemon + projects |
| `PROJECT_LAUNCHER_README.md` | This documentation |

---

## 🎨 Customization

### Change Projects Directory

Edit `project_launcher.py` line 61:
```python
projects_base = Path("C:/Code/projects")  # Change this path
```

### Change Promethean Light Location

Edit `project_launcher.py` line 62:
```python
promethean_dir = Path("C:/Code/Promethian  Light")  # Change this path
```

### Change Startup Command

Edit `project_launcher.py` line 80 and 88:
```python
"cmd.exe", "/k", "echo === {project} === && claude"  # Change command here
```

Examples:
- Git status on start: `"cmd.exe", "/k", "git status && claude"`
- Activate venv: `"cmd.exe", "/k", ".venv\\Scripts\\activate && claude"`
- Custom script: `"cmd.exe", "/k", "python setup.py && claude"`

---

## 🐛 Troubleshooting

### "Windows Terminal not found"
**Solution:** Install Windows Terminal from https://aka.ms/terminal

The launcher will fall back to opening separate `cmd` windows if Windows Terminal isn't available.

### "No projects found"
**Solution:** Make sure `C:\Code\projects` exists and contains folders

### Projects don't show up
**Solution:** Check that project folders don't start with `.` (hidden folders are ignored)

### Claude command not found
**Solution:** Make sure Claude Code CLI is installed and in your PATH
```bash
where claude  # Should show the path to claude.exe
```

---

## 💡 Tips

1. **Select projects you're actively working on** - don't open too many tabs at once
2. **Use Ctrl+Tab** in Windows Terminal to switch between project tabs quickly
3. **Start daemon in background** - Option 1 in START_WITH_PROJECTS.bat keeps it running
4. **Customize for your workflow** - edit the Python script to match your preferences

---

## 🎉 Example Workflow

```bash
# 1. Double-click START_WITH_PROJECTS.bat
# 2. Choose [1] Start Daemon + Launch Projects
# 3. Select projects with Space:
#    ◉ project-sentinel
#    ◉ hr-recruitment
#    ○ business-tools
# 4. Press Enter
# 5. Windows Terminal opens with 3 tabs, Claude ready!
# 6. Start coding immediately 🚀
```

---

## 📝 Notes

- Projects are sorted alphabetically
- Selection is preserved if you re-launch (within the same session)
- Each tab runs independently - closing one doesn't affect others
- Promethean Light daemon runs in background (accessible from any tab)

---

**Happy coding! 🎯**
