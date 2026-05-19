# ML Tracker

Your job is to re-create the multi-agent system we have built in previous workshops. The proposed file structure of the project is:

```bash
ml_tracker/
├── .env                         # your project_id, region, model settings (feel free to copy from `/agent`)
├── __init__.py
├── agent.py                     # root_agent, imports sub-agents
├── registry.py                  # our experiments registry
├── experiment_agent/
│   ├── __init__.py
│   ├── agent.py                 # experiment_agent
│   └── tools.py                 # lookup_experiment 
├── compare_agent/
│   ├── __init__.py
│   ├── agent.py                 # compare_agent
│   └── tools.py                 # compare_experiments
└── deploy_agent/
    ├── __init__.py
    ├── agent.py                 # deploy_agent
    └── tools.py                 # deploy_model
```

You can test out your solution by running 

    ```bash
    uv run adk web --reload_agents --allow_origins="*"
    ```

Make sure `ml_tracker` agent is active and ask few queries:

`Show me the results of experiment EXP-042`
`Compare EXP-042 with EXP-017`
`Deploy EXP-042 to staging`
