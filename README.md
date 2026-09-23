# SF Bike & Bite Planner

An AI-powered casual bike route planning assistant for San Francisco that combines curated food crawls with scenic park picnics and zero-backtracking routing optimization.

Powered by Google DeepMind's Gemini and built with Google Agents SDK / FastAPI.

## Key Features

- **Themed Casual Rides**: Curated and custom food themes (Burrito Trail, Dim Sum & Dumpling Tour, North Beach Slice Quest, Artisanal Scoop & Sun Tour, Golden Gate Glazed Donuts, Waterfront Sourdough & Chowder, etc.).
- **Zero-Backtracking Route Optimization**: TSP (Traveling Salesperson) nearest-neighbor ordering based on geographic coordinates to avoid unnecessary doubling back and hill climbs.
- **Dynamic Group Crawl Controls**: Configurable minimum & maximum food spots (1–8) and park stops (1–5) that dynamically re-query and scale suggestion pools with at least $2\times$ options.
- **Scenic SF Park Stops**: Curated database of 13 bike-friendly San Francisco parks with picnic lawns and panoramic views (Mission Dolores, Presidio Tunnel Tops, Marina Green, Alamo Square, Duboce Park, Crissy Field, etc.).
- **Live Interactive UI**: 3-step planning wizard with split-view candidate selector, Leaflet.js interactive maps, custom venue addition, and turnkey turn-by-turn itinerary exportable to Google Maps Cycling.
- **Store Hours & Timing Verification**: Automatically cross-references opening hours against arrival times for every stop on the tour.

## Project Structure

```
BuildWithGemini/
├── app/
│   ├── agent.py               # Gemini React agent definition & prompts
│   ├── route_tools.py         # Route calculation, TSP optimizer, SF food & park databases
│   ├── fast_api_app.py        # FastAPI server mounting static UI & API endpoints
│   ├── ui_routes.py           # REST endpoints for themes, locations, custom stops & routing
│   ├── static/                # Interactive web frontend (HTML/CSS/JS, Tailwind, Leaflet)
│   └── app_utils/             # Agent runtime and A2A helpers
├── tests/
│   ├── unit/                  # Unit tests for tools, data models, and API endpoints
│   └── integration/           # Integration tests for agent streaming and server E2E
├── GEMINI.md                  # Development guidelines and agent rules
└── pyproject.toml             # Python package dependencies (uv)
```

> 💡 **Tip:** Use [Antigravity CLI](https://antigravity.google/) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **agents-cli**: Agents CLI - Install with `uv tool install google-agents-cli`
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)


## Quick Start

Install `agents-cli` and its skills if not already installed:

```bash
uvx google-agents-cli setup
```

Install required packages:

```bash
agents-cli install
```

Test the agent with a local web server:

```bash
agents-cli playground
```

You can also use features from the [ADK](https://adk.dev/) CLI with `uv run adk`.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agents-cli install` | Install dependencies using uv                                                         |
| `agents-cli playground` | Launch local development environment                                                  |
| `agents-cli lint`    | Run code quality checks                                                               |
| `agents-cli eval`    | Evaluate agent behavior (generate, grade, analyze, and more — see `agents-cli eval --help`) |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests                                                        |
| `agents-cli deploy`  | Deploy agent to Agent Runtime                                                                |
| `agents-cli publish gemini-enterprise` | Register deployed agent to Gemini Enterprise                    || [A2A Inspector](https://github.com/a2aproject/a2a-inspector) | Launch A2A Protocol Inspector                                                        |

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `agents-cli scaffold enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `agents-cli infra cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `agents-cli scaffold upgrade` | Auto-upgrade to latest version while preserving customizations |

---

## Development

Edit your agent logic in `app/agent.py` and test with `agents-cli playground` - it auto-reloads on save.

## Deployment

```bash
gcloud config set project <your-project-id>
agents-cli deploy
```

To add CI/CD and Terraform, run `agents-cli scaffold enhance`.
To set up your production infrastructure, run `agents-cli infra cicd`.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.

## A2A Inspector

This agent supports the [A2A Protocol](https://a2a-protocol.org/). Use the [A2A Inspector](https://github.com/a2aproject/a2a-inspector) to test interoperability.
See the [A2A Inspector docs](https://github.com/a2aproject/a2a-inspector) for details.
