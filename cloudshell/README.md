




# Introduction to Google Agent Development Kit (ADK)

This tutorial walks you through creating your first AI agent using [Google ADK](https://google.github.io/adk-docs/) and extending it with custom tools. We'll use [Cloud Shell](https://cloud.google.com/shell) as our development environment and [Vertex AI](https://cloud.google.com/vertex-ai) as the model backend.

## Prerequisites

- A Google Cloud project with billing enabled
- Access to [Cloud Shell](https://shell.cloud.google.com/) (or a local environment with `gcloud` CLI configured)
- [uv](https://docs.astral.sh/uv/) package manager installed

## Create an agent

Create a new directory for your project and initialize it with `uv`:

```bash
mkdir agent-project
cd agent-project
uv init
```

Add the `google-adk` package:

```bash
uv add google-adk
```

Now scaffold a new agent named `agent`:

```bash
uv run adk create agent
```

The `adk create` command walks you through a few setup questions:

1. **Choose a model** - select `gemini-2.5-flash`. You can always change this later in the generated `agent.py` file.
2. **Choose a backend** - select **Vertex AI** to access the model through Google Cloud.
3. **Confirm your Google Cloud project** - if you have `gcloud` configured, it suggests your default project and a region. If the wizard defaults to `us-central1`, consider changing it to `global`.

> **Tip:** You can switch between models in `.env` file. Keep in mind that preview models on Vertex AI are provided as-is and could undergo non-backwards-compatible changes.

The command creates a new `agent/` directory with several files, including `agent.py`:

```python
from google.adk.agents import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
```

## Start the ADK in CLI

Launch the Agent with command

```bash
uv run adk run agent
```

You may notice some warnings about [EXPERIMENTAL] features user for `InMemoryCredentialService`. We can ignore those now.

Ask a question or two. When ready to leave, type `exit` and press Enter.

## Start the ADK web UI

Launch the ADK web UI with hot-reloading enabled. Since we're using Cloud Shell, we need the `--allow_origins="*"` flag for the Web Preview feature to work:

```bash
uv run adk web --reload_agents --allow_origins="*"
```

This starts a local web server and opens the ADK web UI in your browser. The `--reload_agents` flag makes sure that any changes you make to your agent's code are automatically picked up by the server. You can now chat with your agent.

## Adding tools to your agent

Agents become much more useful when they can interact with the outside world. By adding tools, you give your agent the ability to fetch real-time data, call APIs, and perform tasks beyond basic text generation.

### Example: a URL fetcher tool

Let's create a Python function that fetches the content of a URL and add it to the agent's toolbox.

Install the `httpx` library. From your `agent-project` directory:

```bash
uv add httpx
```

Let's add `fetch_url` tool that will give our agent capabilities to fetch the content of given URL. The simplest code for such function could be:

```python
import httpx

def fetch_url(url: str) -> str:
    """Fetches the content of a URL."""
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
```

You can test the function by running from `cloudshell/` directory:
```bash
uv run python fetch.py
```

This will fetch https://www.example.com and extract the content of first `h1` header.

Based on what you lernt from previous workshops, update `agent/agent.py`  to enable agent to use a `fetch_url` tool. (feel free to copy over fetch_url code)
Now update to look like this:

The key parts:

- The `fetch_url` function is a regular Python function. ADK uses the function signature and docstring to tell the model what the tool does and how to call it.
- The `tools=[fetch_url]` parameter registers the function as an available tool for the agent.

### Test your tool

1. Start (or restart) the web UI:
    
    ```bash
    uv run adk web --reload_agents --allow_origins="*"
    ```
    
2. If the server was already running, click **New Session** in the top right of the ADK web interface to reload the latest agent code.
    
3. In the chat interface, ask the agent to fetch and summarize a URL, for example: "Give me quote from https://altl.io/"
    

The agent should call `fetch_url` behind the scenes and use the returned content to answer your question.


