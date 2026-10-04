---
title: "uv: The Tool That Helps You Manage Your Python Project Dependencies Smoothly"
subtitle: ""
date: "2025-08-31"
url: "https://ricardoheredia.substack.com/p/uv-the-tool-that-helps-you-manage"
slug: "uv-the-tool-that-helps-you-manage"
wordcount_substack: 1217
reactions: 5
restacks: 1
comments: 2
---

If you've been working with Python for a while, you've probably experienced the frustration when you're trying to set up a project and you're dealing with conflicting package versions, virtual environment headaches, or waiting forever for pip or Conda to resolve dependencies.

We've all been there.

But fortunately there's a tool that can solve all of these problems in second.

**uv** is the Python package that's helps setting up and managing Python projects blazingly fast.

## What is uv?

Is a Python package manager built in Rust that promises to be "an extremely fast Python package installer and resolver."

uv was created by the team at Astral (the same people behind Ruff), and it's designed to replace not just pip, but also pipenv, poetry, pyenv, and conda in many use cases. It's a unified tool that handles:

- Package installation and resolution

- Virtual environment management

- Python version management

- Project scaffolding

Think of it as the Swiss Army knife for Python development, but one that actually works smoothly instead of having unstable tools.

[![](https://substackcdn.com/image/fetch/$s_!fmvg!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9e4c9d5e-db89-4659-b2d2-44a6229481da_1350x578.heic)](https://substackcdn.com/image/fetch/$s_!fmvg!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9e4c9d5e-db89-4659-b2d2-44a6229481da_1350x578.heic)

## Why uv Beats Everything Else

### Speed

Where uv really shines. While pip can take minutes to install a complex set of dependencies, uv does it in seconds. We're talking about 10-100x faster installation times.

The first time you use it, you'll think something went wrong because it finished too quickly (happened to me).

### Better Than pip

pip is the default, but it's also slow and doesn't handle dependency resolution as elegantly as it could.

uv uses a modern resolver that's both faster and more reliable. Plus, unlike pip, uv creates isolated environments by default.

### Simpler Than Poetry

Poetry is great for dependency management, but it has its quirks. The configuration can be complex, and it sometimes feels like overkill for simple projects.

> **uv gives you the power of Poetry with the simplicity of pip.**

### More Reliable Than Conda

Conda has its place, it was the first package manager I used, especially for scientific computing and data science. But for pure Python projects, Conda environments can be heavy and sometimes unpredictable, they can easily break and sometimes trying to find the root of that error and fixing it is worse than creating a new environment from scratch.

uv keeps things lightweight and consistent.

## What Makes uv Special: The Technical Bits

When you use uv, you get three key files that make your life easier:

### 1\. pyproject.toml

This is your project's configuration file. It contains all your dependencies, project metadata, and build settings in a standardized format. Unlike requirements.txt, it separates development dependencies from production ones and includes version constraints clearly.

When you run `uv pip install` in a project with a `pyproject.toml` file, `uv` will:

1. **Read Dependencies**: Automatically detect and install the dependencies listed in the `[project]` and `[project.optional-dependencies]` sections.

2. **Manage Environments**: Create and sync a virtual environment with the exact dependencies specified in the `uv.lock` file (if present) or `pyproject.toml`.

3. **Lock Dependencies**: Generate a `uv.lock` file that pins the versions of all direct and transitive dependencies, ensuring fully reproducible builds.

This makes `uv` a powerful tool for managing complex projects without needing higher-level workflow managers.

### 2\. uv.lock

It contains the exact versions of every package (and their dependencies) that your project uses. This means when someone else runs your project, they get the exact same package versions you used. Helps to avoid the "but it works on my machine" issues.

### 3\. Automatic .venv Creation

uv automatically creates and manages virtual environments. No more remembering to activate environments or wondering which packages belong to which project.

`uv` streamlines virtual environment creation and management.

- **Creating a virtual environment**:

```
# Creates a .venv directory in the current folder
uv venv
```

This command automatically finds your system's Python and creates a virtual environment. To use a specific Python version, use the `--python` flag (e.g., `uv venv --python 3.11`).

- **Activating the virtual environment**:

Activation commands remain standard for your shell:

```
# For bash or zsh
source .venv/bin/activate
```

Once a virtual environment is active, `uv` commands like `uv pip install` will automatically use it.

## The Modern Data Stack Connection

If you're working in data science or analytics (for example in football analytics), uv is particularly valuable regarding:

- **Reproducible analyses**: The lock file ensures your analysis can be reproduced exactly

- **Faster iteration**: Quick environment setup means less time waiting, more time analyzing

- **Clean project structure**: Clear separation between development and production dependencies

- **Better collaboration**: Team members can quickly get identical environments

## Real Example: Setting Up My Football Analytics Project

Here’s an example on how to get started with my football analytics tutorials repository using uv.

### Step 1: Install uv

```
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip if you prefer
pip install uv
```

### Step 2: Clone and Set Up the Project

```
git clone https://github.com/ricardoheredia/football-analytics-tutorials.git
cd football-analytics-tutorials
```

Now, instead of dealing with virtual environments, requirements files, and all that complexity, you just run:

```
uv sync
```

And uv will:

- Create a virtual environment automatically

- Install all dependencies from the lock file

- Ensure everything is isolated

- Do it all in seconds

### Step 3: Start Working

```
uv run jupyter notebook
```

This command runs Jupyter in the project's environment without you having to manually activate it.

## The Files That Make It Work

In the repo, you'll see these key files:

**pyproject.toml** contains our project configuration:

```
[project]
name = "football-analytics-tutorials"
dependencies = [\
    "pandas>=2.0.0",\
    "matplotlib>=3.7.0",\
    "seaborn>=0.12.0",\
    "jupyter>=1.0.0",\
    # ... more dependencies\
]

[project.optional-dependencies]
dev = [\
    "pytest>=7.0.0",\
    "black>=23.0.0",\
]
```

**uv.lock** ensures everyone gets the exact same package versions (this file is quite long, but that's the point – it's comprehensive).

[![](https://substackcdn.com/image/fetch/$s_!NE2R!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F86495572-c6f7-4317-a944-7da0f9380d95_750x612.heic)](https://substackcdn.com/image/fetch/$s_!NE2R!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F86495572-c6f7-4317-a944-7da0f9380d95_750x612.heic)

## Why This Matters for Your Workflow

Using uv has changed how I approach new projects. Instead of spending minutes setting up environments and installing packages, I spend a few seconds. It helps removing the friction that often prevents us from starting new experiments or sharing our work.

Now, if I want to test a football analytics technique, I can:

1. Create a new project with `uv init`

2. Add dependencies with `uv add pandas matplotlib`

3. Start coding immediately

## Getting Started Today

If you want to try this out with the example repository:

1. Install uv using one of the methods above

2. Clone the repo: `git clone https://github.com/ricardoheredia/football-analytics-tutorials.git`

3. Run `uv sync`

4. Start exploring: `uv run jupyter notebook`

[![](https://substackcdn.com/image/fetch/$s_!eZGr!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa918ebd0-d32d-468c-8257-462f30b4bb07_2774x1536.heic)](https://substackcdn.com/image/fetch/$s_!eZGr!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa918ebd0-d32d-468c-8257-462f30b4bb07_2774x1536.heic)

Check the documentation from the website if you want to go deeper: [uv documentation](https://docs.astral.sh/uv/)

You'll be up and running under a minute.

## The Bottom Line

Python package management has been a pain point for too long.

uv solves the problem and makes the whole experience smooth. Fast installation, reliable dependency resolution, and automatic environment management mean less time fighting with tools.

For football analytics, data science, machine learning, or any Python project, uv is rapidly becoming the standard.

The combination of speed, reliability, and simplicity is hard to beat.

* * *

Let me know in the comments if you have already tried it before or what’s your preferred Python package manager.

**Check out the [tutorials repository](https://github.com/ricardoheredia/football-analytics-tutorials) and start building your own match analysis dashboards today**

Thanks for reading The NetPass! This post is public so feel free to share it with anyone you think might like reading about data, AI/ML, football analytics and more.

[Share](https://ricardoheredia.substack.com/p/uv-the-tool-that-helps-you-manage?utm_source=substack&utm_medium=email&utm_content=share&action=share)

Till next time,

Ricardo.

[![Ricardo Heredia's avatar](https://substackcdn.com/image/fetch/$s_!ddIT!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6d582183-8bb5-43cc-ab1a-620ca5f196c5_1200x1500.jpeg)](https://substack.com/profile/313134153-ricardo-heredia)[![Dillon's avatar](https://substackcdn.com/image/fetch/$s_!owZm!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F678c0509-67cd-44a8-adb3-006fc6abf50f_144x144.png)](https://substack.com/profile/165733874-dillon)[![Iain's avatar](https://substackcdn.com/image/fetch/$s_!pVFH!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F748d34d8-be34-48c6-8279-84728e3cd48e_144x144.png)](https://substack.com/profile/136140576-iain)[![Shanice's avatar](https://substackcdn.com/image/fetch/$s_!1-80!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa22ddb73-bea8-4a0d-bde5-f361135a3a4a_1080x1080.jpeg)](https://substack.com/profile/64878913-shanice)

5 Likes∙
