# GenAI Crash Course - Google ADK

Welcome to GenAI Crash Course - Google ADK part!

This repository contains two sections. 

# Google ADK in Jupyter Notebook

1. Connect to Agent Platform workbench - https://console.cloud.google.com/agent-platform/workbench/instances 
2. open terminal and clone the repository
```bash
git clone https://github.com/deepsense-ai/genai_crash_course_google_adk.git
```
3. Open notebook: `notebooks/adk_notebook.ipynb` and follow the instructions

# Google ADK in Cloud Shell

1. Open Cloud Shell and clone the repository
```bash
git clone https://github.com/deepsense-ai/genai_crash_course_google_adk.git
```
2. navigate to `cloudshell` directory
```bash
cd genai_crash_course_google_adk/cloudshell/
```
3. Open `cloudshell/README.md` and follow the instructions.


## Updated `call_agent` definition

```python

async def call_agent(query: str, runner: Runner, user_id: str, session_id: str):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User: {query}")

    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response = "Agent did not produce a final response."

    async with contextlib.aclosing(runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    )) as stream:
        async for event in stream:
            # this is only for 'workshop' to increase vistibility
            if event.author and event.content and event.content.parts:
                if event.author and event.content and event.content.parts:
                    part = event.content.parts[0]
                    if part.function_call:
                        print(f"  [{event.author}]: (tool call: {part.function_call.name})...")
                    elif part.text:
                        print(f"  [{event.author}]: {part.text[:80]}...")
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response = f"Agent escalated: {event.error_message or 'No details.'}"
            

    print(f"<<< Agent: {final_response}")
```
