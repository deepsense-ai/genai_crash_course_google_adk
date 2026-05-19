# Introduction to Google Agent Development Kit (ADK) in CloudShell

This tutorial walks you through creating your first AI agent using [Google ADK](https://google.github.io/adk-docs/) and extending it with custom tools. We'll use [Cloud Shell](https://cloud.google.com/shell) as our development environment and [Vertex AI](https://cloud.google.com/vertex-ai) as the model backend.

## Prerequisites

- A Google Cloud project with billing enabled
- Access to [Cloud Shell](https://shell.cloud.google.com/) (or a local environment with `gcloud` CLI configured)
- [uv](https://docs.astral.sh/uv/) package manager installed

## Create an agent

Make sure you are in `cloudshell` directory and initialize it with `uv`:

```bash
uv init
```

Add the `google-adk` package:

```bash
uv add google-adk
```

Now scaffold a new agent named `agent`:

```bash
uv run adk create myagent
```

The `adk create` command walks you through a few setup questions:

1. **Choose a model** - select `gemini-2.5-flash`. You can always change this later in the generated `agent.py` file.
2. **Choose a backend** - select **Vertex AI** to access the model through Google Cloud.
3. **Confirm your Google Cloud project** - if you have `gcloud` configured, it suggests your default project and a region. If the wizard defaults to `us-central1`, consider changing it to `global`.

> **Tip:** You can switch between models in `.env` file. Keep in mind that preview models on Vertex AI are provided as-is and could undergo non-backwards-compatible changes.

The command creates a new `myagent/` directory with several files, including `agent.py`:

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
uv run adk run myagent
```

You may notice some warnings about [EXPERIMENTAL] features user for `InMemoryCredentialService`. We can ignore those now.

Ask a question or two. When ready to leave, type `exit` and press Enter.

## Start the ADK web UI

Launch the ADK web UI with hot-reloading enabled. Since we're using Cloud Shell, we need the `--allow_origins="*"` flag for the Web Preview feature to work:

```bash
uv run adk web --reload_agents --allow_origins="*"
```

This starts a local web server and opens the ADK web UI in your browser. The `--reload_agents` flag makes sure that any changes you make to your agent's code are automatically picked up by the server. You can now chat with your agent. **Make sure you choose `myagent`**  in top left part of the GUI (`Select an app`).

## Adding tools to your agent

Agents become much more useful when they can interact with the outside world. By adding tools, you give your agent the ability to fetch real-time data, call APIs, and perform tasks beyond basic text generation.

### Example: a URL fetcher tool

Let's create a Python function that fetches the content of a URL and add it to the agent's toolbox.

Install the `httpx` library. From your `cloudshell` directory:

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

Based on what you lernt from previous workshops, update `myagent/agent.py`  to enable agent to use a `fetch_url` tool. (feel free to copy over fetch_url code)
Now update to look like this:

The key parts:

- The `fetch_url` function is a regular Python function. ADK uses the function signature and docstring to tell the model what the tool does and how to call it.
- The `tools=[fetch_url]` parameter registers the function as an available tool for the agent.

### Test your tool

1. Start (or restart) the web UI:
    
```bash
uv run adk web agent --reload_agents --allow_origins="*"
```
    
2. If the server was already running, click **New Session** in the top right of the ADK web interface to reload the latest agent code.
    
3. In the chat interface, ask the agent to fetch and summarize a URL, for example: "Give me quote from https://altl.io/"
    

The agent should call `fetch_url` behind the scenes and use the returned content to answer your question.


## Task 2 - recreate a ml_tracker

Navigate to ml_tracker directory and check out README.md for more instructions

## Task 3 - loop agent

Let's use the example from the documentation - https://adk.dev/agents/workflow-agents/loop-agents/

1. Create a `loop_agent` directory and populate it with `.env` file (remember about the content)
2. Create a `agent.py` with content:

```python
from google.adk.agents import LoopAgent, LlmAgent, SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext

# --- Constants ---
GEMINI_MODEL = "gemini-2.5-flash"

# --- State Keys ---
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No major issues found."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}

# --- Before Agent Callback ---
def update_initial_topic_state(callback_context: CallbackContext):
    """Ensure 'initial_topic' is set in state before pipeline starts."""
    callback_context.state['initial_topic'] = callback_context.state.get('initial_topic', 'a robot developing unexpected emotions')

# --- Agent Definitions ---

# STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    instruction=f"""
    You are a Creative Writing Assistant tasked with starting a story.
    Write a *very basic* first draft of a short story (just 1-2 simple sentences).
    Keep it plain and minimal - do NOT add descriptive language yet.
    Topic: {{initial_topic}}

    Output *only* the story/document text. Do not add introductions or explanations.
    """,
    description="Writes the initial document draft based on the topic, aiming for some initial substance.",
    output_key=STATE_CURRENT_DOC
)

# STEP 2a: Critic Agent (Inside the Refinement Loop)
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    instruction=f"""
    You are a Constructive Critic AI reviewing a short story draft.

    **Document to Review:**
    ```
    {{current_document}}
    ```

    **Completion Criteria (ALL must be met):**
    1. At least 4 sentences long
    2. Has a clear beginning, middle, and end
    3. Includes at least one descriptive detail (sensory or emotional)

    **Task:**
    Check the document against the criteria above.

    IF any criteria is NOT met, provide specific feedback on what to add or improve.
    Output *only* the critique text.

    IF ALL criteria are met, respond *exactly* with: "{COMPLETION_PHRASE}"
    """,
    description="Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
    output_key=STATE_CRITICISM
)

# STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    # Relies solely on state via placeholders
    include_contents='none',
    instruction=f"""
    You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
    **Current Document:**
    ```
    {{current_document}}
    ```
    **Critique/Suggestions:**
    {{criticism}}

    **Task:**
    Analyze the 'Critique/Suggestions'.
    IF the critique is *exactly* "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

    Do not add explanations. Either output the refined document OR call the exit_loop function.
    """,
    description="Refines the document based on critique, or calls exit_loop if critique indicates completion.",
    tools=[exit_loop], # Provide the exit_loop tool
    output_key=STATE_CURRENT_DOC # Overwrites state['current_document'] with the refined version
)

# STEP 2: Refinement Loop Agent
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=5 # Limit loops
)

# STEP 3: Overall Sequential Pipeline
# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = SequentialAgent(
    name="IterativeWritingPipeline",
    sub_agents=[
        initial_writer_agent, # Run first to create initial doc
        refinement_loop       # Then run the critique/refine loop
    ],
    before_agent_callback=update_initial_topic_state, # set initial topic in state
    description="Writes an initial document and then iteratively refines it with critique using an exit tool."
)
```

3. Run the agent and try to ask about random story, such as `a cat that secretly runs a city at night`.
