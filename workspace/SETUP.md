# Course workspace setup

This guide sets up everything you need for all five exercises, on your own laptop. You only do it **once**, at the start of the course.

- **Time:** about 45–60 minutes, mostly waiting for downloads.
- **Cost:** nothing. Every tool here is free, and you never need a paid subscription or API credits.
- **Disk space:** about 4 GB, most of it for the AI model.
- **Your laptop:** Windows 10/11, macOS 12 or newer, or Linux, with at least **8 GB of RAM** for the real model. Less than that is OK too; see step 8.

> **Commands.** Lines in grey boxes are commands to type in a terminal. On **Windows**, use **PowerShell** (Start menu → type "PowerShell"). On **macOS**, use **Terminal** (Applications → Utilities). On **Linux**, use any terminal. After step 7, always run commands from the **top folder of your course repository**.

## Checklist

| # | Step | Account needed? |
|---|---|---|
| 1 | Create a GitHub account | **Yes**, free |
| 2 | Install Git | No |
| 3 | Install GitHub CLI and sign in | Uses your GitHub account |
| 4 | Install Python 3.11+ | No |
| 5 | Install VS Code (recommended) | No |
| 6 | Create your private course repository from the template | Uses your GitHub account |
| 7 | Create a virtual environment and install pytest | No |
| 8 | Install Ollama and download the model | No |
| 9 | Run the smoke test | — |

Step 10 explains how to save your work, step 11 how to submit an exercise, and step 12 how to get each new exercise.

---

## 1. Create a GitHub account

GitHub stores your code online. You'll submit every exercise as a link to your GitHub repository.

1. Go to **https://github.com/signup**.
2. Enter your email (your university email is best), a password and a username. **Your username will appear in your submission links**, so pick something sensible.
3. Verify your email: GitHub sends you a code, and you enter it on the page.
4. Turn on two-factor authentication when GitHub asks. It's required for everyone who pushes code (help: https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa).
5. *(Optional, free for students)* Apply for the **GitHub Student Developer Pack** at https://education.github.com/pack. You don't need it for this course.

Already have an account? You can use it. Just make sure you can sign in.

## 2. Install Git

Git saves versions of your code and sends them to GitHub.

| System | How |
|---|---|
| **Windows** | Download from **https://git-scm.com/download/win** and run the installer. **Keep every default option**; it includes "Git Credential Manager", which handles GitHub sign-in for you. |
| **macOS** | Run `xcode-select --install` in Terminal and click *Install*. Alternatives: https://git-scm.com/download/mac |
| **Linux** | Debian/Ubuntu: `sudo apt update && sudo apt install git`. Fedora: `sudo dnf install git`. |

Close and reopen your terminal, then tell Git who you are (use the same email as your GitHub account):

```
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

`git --version` should print something like `git version 2.4x`.

## 3. Install GitHub CLI and sign in

The GitHub CLI (`gh`) connects your laptop to your GitHub account, so `git push` works without typing passwords.

| System | How |
|---|---|
| **Windows** | `winget install --id GitHub.cli`, or download the installer from **https://cli.github.com** |
| **macOS** | Download from **https://cli.github.com**, or if you use Homebrew: `brew install gh` |
| **Linux** | Follow **https://github.com/cli/cli/blob/trunk/docs/install_linux.md** |

Close and reopen the terminal, then sign in:

```
gh auth login
```

Answer the questions like this:
- *Where do you use GitHub?* → **GitHub.com**
- *Preferred protocol?* → **HTTPS**
- *Authenticate Git with your GitHub credentials?* → **Yes**
- *How would you like to authenticate?* → **Login with a web browser**. Copy the one-time code it shows, press Enter, and paste the code in the browser.

Check that it worked: `gh auth status` should say "Logged in to github.com".

## 4. Install Python 3.11 or newer

| System | How |
|---|---|
| **Windows** | Download "Python 3.12" (or newer) from **https://www.python.org/downloads/**. In the installer, **tick "Add python.exe to PATH"** at the bottom of the first screen, then click *Install Now*. |
| **macOS** | Download the macOS installer from **https://www.python.org/downloads/** and run it. |
| **Linux** | Ubuntu 24.04 and newer already include Python 3.12: `sudo apt install python3 python3-venv python3-pip`. On older systems, see https://www.python.org/downloads/. |

Check the version (close and reopen the terminal first):

- Windows: `python --version` (if that opens the Microsoft Store or fails, try `py --version`)
- macOS/Linux: `python3 --version`

It must say **3.11** or higher.

## 5. Install VS Code (recommended)

Any editor works. VS Code is free and makes Python easier.

1. Download from **https://code.visualstudio.com/** and install it.
2. Open VS Code, click the **Extensions** icon on the left (four squares), search for **"Python"**, and install the extension published by **Microsoft**: https://marketplace.visualstudio.com/items?itemName=ms-python.python

## 6. Create your private course repository

You get your own copy of the course code from a **template**, keep it **private**, and give the instructor read access so your work can be graded.

1. Open the course template: **https://github.com/alexsherba29/agentic-ai-course-student**
2. Click the green **Use this template** button, then **Create a new repository**.
3. Fill in:
   - **Owner:** your username
   - **Repository name:** `agentic-ai-course`
   - Visibility: **Private**. ⚠️ Public repositories let other students copy your work.
4. Click **Create repository**.
5. Give the instructor access: in your new repository, open **Settings → Collaborators** (left menu) → **Add people** → type **`alexsherba29`** → **Add**. *Without this step your submissions can't be graded.* GitHub sends the instructor an invitation, which they accept on their side; you don't need to do anything else. (Personal repositories don't offer a read-only role, so the instructor technically gets write access. They only read and never push to your repository.)
6. Download (clone) it to your laptop. Choose a folder you'll remember, for example your Documents folder:
   ```
   cd ~/Documents
   gh repo clone YOUR-USERNAME/agentic-ai-course
   cd agentic-ai-course
   ```
   On Windows PowerShell, `cd ~/Documents` works too.

From now on, **every command in this course is run inside this `agentic-ai-course` folder.** In VS Code, use *File → Open Folder…* and choose it.

## 7. Create a virtual environment and install pytest

A virtual environment keeps this course's Python packages separate from everything else on your laptop.

Create it once:

- Windows: `python -m venv .venv` (or `py -m venv .venv`)
- macOS/Linux: `python3 -m venv .venv`

**Activate it every time you open a new terminal for the course:**

| System | Command |
|---|---|
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |
| macOS/Linux | `source .venv/bin/activate` |

You'll see `(.venv)` at the start of the prompt. Once it's active, **`python` means the right Python on every system.**

> Windows error "running scripts is disabled on this system"? Run this once, then try again: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Install the only package the course needs:

```
python -m pip install -r workspace/requirements.txt
```

VS Code tip: press `Ctrl+Shift+P` (macOS: `Cmd+Shift+P`) → *Python: Select Interpreter* → choose the one in `.venv`.

## 8. Install Ollama and download the model

Ollama runs a real, free, open AI model **on your own laptop**. No account and no internet are needed once the model is downloaded.

1. Download and install Ollama from **https://ollama.com/download** :
   - **Windows / macOS:** run the installer. Ollama then runs in the background (look for the llama icon in the taskbar or menu bar).
   - **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`
2. Download the course model (about 2 GB, a one-time download):
   ```
   ollama pull llama3.2:3b
   ```
3. Try it:
   ```
   ollama run llama3.2:3b "Say hello in one sentence."
   ```
   The first answer can take up to a minute while the model loads; later ones are faster.

**If your laptop is slow or runs out of memory**, use the smaller model:

```
ollama pull qwen2.5:1.5b
```

Then tell the course code to use it. Set this in each new terminal, after activating `.venv`:

| System | Command |
|---|---|
| Windows PowerShell | `$env:OLLAMA_MODEL = "qwen2.5:1.5b"` |
| macOS/Linux | `export OLLAMA_MODEL=qwen2.5:1.5b` |

**If Ollama can't run on your laptop at all**, don't worry. Every exercise and **every test** also works with the course's *fake model*, which follows a fixed script. You'll do all the tasks the same way; you just won't see a real model's answers. Tell the instructor so they know.

## 9. Run the smoke test

With `.venv` active, from the `agentic-ai-course` folder:

```
python workspace/smoke_test.py
```

You should see something like:

```
✅ Python 3.12.3
✅ pytest 8.3.2
✅ course code works with the fake model
✅ git repo, origin = https://github.com/YOUR-USERNAME/agentic-ai-course.git
✅ Ollama is running at http://localhost:11434
✅ model llama3.2:3b is downloaded
✅ the model chose a tool: check_service_status({'service': 'vpn'})

READY — your workspace works. 🎉
```

- ⚠️ lines are hints. The workspace still works.
- ❌ lines must be fixed. Each one tells you what to do; see the troubleshooting table below.
- Without Ollama, run `python workspace/smoke_test.py --fake-only`.

## 10. Saving your work

Your code is only safe once it's on GitHub. At the end of every session:

```
git add -A
git commit -m "Exercise 01: finished step 2"
git push
```

Each exercise builds on **your own code** from the previous one, so keep everything in this one repository and don't delete earlier exercises.

## 11. How to submit an exercise

Each exercise is submitted separately, as a **link to that exercise's folder** at a **tag**. A tag is a bookmark on one exact version of your code.

1. Make sure the public tests pass, for example for exercise 01:
   ```
   python -m pytest exercises/01-first-agent/tests
   ```
2. Save and push your work (step 10).
3. Create and push the tag for this exercise (`ex01-submit`, `ex02-submit`, … `ex05-submit`):
   ```
   git tag ex01-submit
   git push origin ex01-submit
   ```
4. Your submission link is:
   ```
   https://github.com/YOUR-USERNAME/agentic-ai-course/tree/ex01-submit/exercises/01-first-agent
   ```
   Open it in your browser to check that it shows your code. Then paste it into the course submission form: **(the instructor will announce the form link)**

**Changed something after tagging, before the deadline?** Move the tag to your newest commit:

```
git tag -f ex01-submit
git push -f origin ex01-submit
```

Grading uses the commit the tag points to at grading time, and records that commit's date. **The link must point to the right exercise:** an `ex02` link in the exercise 01 form can't be graded.

## 12. Getting a new exercise

New exercises are released one at a time in the course template. To add one to your repository **without touching your own code**:

```
git remote add course https://github.com/alexsherba29/agentic-ai-course-student.git
git fetch course
git checkout course/main -- common exercises/02-docs-agent
git commit -m "Add exercise 02"
git push
```

Run the `git remote add` line only the first time. After that, `git fetch course` and the `checkout` line are enough, with the new exercise's folder name. It copies the new exercise and the latest shared course code in `common/` (which you never edit). Your earlier exercises stay exactly as you left them.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` / `git` / `gh` / `ollama`: "command not found" or "not recognized" | Close and reopen the terminal after installing. On Windows, re-run the Python installer and tick "Add python.exe to PATH". |
| `python` opens the Microsoft Store (Windows) | Use `py` instead of `python` until `.venv` is active, or turn off *Settings → Apps → Advanced app settings → App execution aliases → python*. |
| `No module named pytest` | Activate `.venv` (step 7), then run `python -m pip install -r workspace/requirements.txt`. |
| `cannot import the course code` | You're in the wrong folder. `cd` into `agentic-ai-course` (the folder that contains `common/` and `exercises/`). |
| `Could not reach Ollama` | Start the Ollama app (Windows/macOS), or run `ollama serve` in a separate terminal (Linux). |
| `model 'llama3.2:3b' is not downloaded` | `ollama pull llama3.2:3b` (or set `OLLAMA_MODEL` to the model you downloaded). |
| The model is very slow or the laptop freezes | Close other programs, or switch to `qwen2.5:1.5b` (step 8). |
| `git push` asks for a password | Run `gh auth login` again (step 3). GitHub doesn't accept account passwords for git. |
| `remote: Repository not found` when pushing | Check that you cloned *your* repository (`git remote -v`), not the course template. |
| The submission link shows "404" | Check that you pushed the tag (`git push origin ex01-submit`), that the folder name is correct, and that the instructor is a collaborator (step 6.5). |

Still stuck? Post the full error message (copy the text; a screenshot is OK too) on the course forum.
