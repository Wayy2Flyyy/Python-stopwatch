# Task Stopwatch

I built this stopwatch to track how much time I spend on different applications throughout the day. It's been really useful for understanding where my time goes.

## What I Added

I wanted something more than just a basic timer, so I added:

- **Automatic app detection** - It scans your running applications and lets you pick which one to track
- **Lap times** - You can mark checkpoints during a session, and it highlights your fastest/slowest laps
- **Session history** - Everything gets saved automatically so you can look back at what you worked on
- **Clean interface** - Dark theme because I like it, and I filtered out all the system junk so you only see actual apps

The filtering was important to me - I didn't want to see 50 Windows processes cluttering the dropdown. Now it only shows the apps you'd actually care about tracking.

## Requirements

- Python 3.7+
- Windows (I used psutil for process detection)

## Requirements

- Python 3.7+
- Windows (I used psutil for process detection)

## Setup

Clone it and set up a virtual environment:

```bash
git clone https://github.com/yourusername/gaming-stopwatch.git
cd gaming-stopwatch
python -m venv .venv
```

Activate the virtual environment:

**PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

Install dependencies:
```bash
pip install -r requirements.txt
```

If that doesn't work, just install psutil directly:
```bash
pip install psutil
```

## Running It

If you activated the virtual environment:
```bash
python stopwatch.py
```

Or run it directly:
```powershell
.venv\Scripts\python.exe stopwatch.py
```

## How to Use

1. Hit the refresh button to scan for running apps
2. Pick the app you want to track from the dropdown
3. Click START
4. Hit LAP whenever you want to mark a checkpoint
5. Click STOP when you're done (saves automatically)
6. Check out your history by clicking "View History"

The fastest lap shows up in green, slowest in red. I thought that was a nice touch.

The fastest lap shows up in green, slowest in red. I thought that was a nice touch.

## Troubleshooting

**psutil won't install?**

Try this:
```bash
pip install --only-binary :all: psutil
```

This grabs a pre-built version instead of trying to compile it.

**Dropdown is empty?**

Click refresh and make sure you have some apps open. I filter out system processes, so if you only have Windows stuff running, you won't see much.

**PowerShell won't let you activate the venv?**

Run this:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Customization

Want to add more apps to the priority list? Edit `app_keywords` in `stopwatch.py`:

```python
self.app_keywords = [
    'game', 'steam', 'chrome', 'code',
    # add whatever
]
```

Need to exclude something? Add it to `excluded_processes`:

```python
self.excluded_processes = [
    'svchost', 'system',
    # add processes you don't want
]
```

## Data

Session data goes into `task_history.json`. It gets created automatically when you stop your first session.

## Contributing

If you find bugs or want to add features, feel free to open an issue or PR.

---

Built this because I wanted to see where my time was actually going. Hope it helps you too.
