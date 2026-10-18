# Agentic AI — course workspace

This is your personal copy of the practical part of the Agentic AI course. Over five exercises you'll build one **IT-support agent** in plain Python. Each exercise adds a new ability on top of your own code from the previous one.

| # | Exercise | Folder |
|---|---|---|
| 01 | My first agent | [`exercises/01-first-agent/`](exercises/01-first-agent/README.md) |

New exercises appear here as they're released. The instructor will tell you how to pull them into your repository.

## Start here

1. Follow **[`workspace/SETUP.md`](workspace/SETUP.md)** once. It covers accounts, installs, the AI model, creating your private repository, and how to submit.
2. Check your setup: `python workspace/smoke_test.py`
3. Open the first exercise's `README.md` and follow its tasks.

## How this repository is organised

- `exercises/NN-name/README.md`: the instructions for each exercise.
- `exercises/NN-name/starter/`: **your code**. This is the only folder you edit, plus `answers.md` where an exercise asks for one.
- `exercises/NN-name/tests/`: the public tests (`python -m pytest exercises/NN-name/tests`). Don't edit them: grading uses its own copy.
- `common/`: shared course code: the model interface, a scripted fake model, and mock IT systems. Read it, but don't change it.
- `workspace/`: the setup guide and the smoke test.

## Submitting

Each exercise is submitted as a link to its folder at a tag, for example:
`https://github.com/<you>/<repo>/tree/ex01-submit/exercises/01-first-agent`
The full steps are in `workspace/SETUP.md`, step 11.
