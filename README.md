# Course Creation Agent (Distributed)

A multi-agent system built with Google's Agent Development Kit (ADK) and Agent-to-Agent (A2A) protocol. It features a team of microservice agents that research, judge, and build content, orchestrated to deliver high-quality results.

## Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Developer Guide](#developer-guide)
- [Contributing](#contributing)

## Architecture

This project uses a distributed microservices architecture where each agent runs in its own container and communicates via A2A:

*   **Orchestrator Service (`orchestrator/`):** The main entry point. It manages the workflow using `LoopAgent` and `SequentialAgent`, and connects to other agents using `RemoteA2aAgent`. It also serves the frontend.
*   **Researcher Service (`researcher/`):** A standalone agent that gathers information using Google Search.
*   **Judge Service (`judge/`):** A standalone agent that evaluates research quality.
*   **Content Builder Service (`content_builder/`):** A standalone agent that compiles the final course.

The system follows a "Research -> Judge -> Build" pipeline:

1.  **Research Loop:**
    *   The **Researcher** gathers information based on the user's topic.
    *   The **Judge** evaluates the findings.
    *   If the Judge fails the findings, the loop repeats with feedback.
    *   If the Judge passes, the loop terminates.
2.  **Content Building:**
    *   The **Content Builder** takes the approved research and creates a structured course.

## Project Structure

```
course-creation-agent/
├── orchestrator/        # Main service (orchestration + frontend)
│   ├── app/
│   │   ├── agent.py               # Agent definitions and workflow logic
│   │   ├── server.py              # FastAPI server and endpoints
│   │   ├── simple_remote_agent.py # HTTP client for remote agents
│   │   └── utils/
│   ├── frontend/        # Web UI
│   └── Dockerfile
├── researcher/          # Researcher microservice
│   ├── app/
│   └── Dockerfile
├── judge/               # Judge microservice
│   ├── app/
│   └── Dockerfile
├── content_builder/     # Content Builder microservice
│   ├── app/
│   └── Dockerfile
├── Makefile             # Command shortcuts
└── ...
```

## Prerequisites

*   **Python 3.10+**
*   **uv**: Python package manager (required for local development).
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
*   **Google Cloud SDK**: For GCP services and authentication.
    ```bash
    gcloud auth application-default login
    ```
*   **Google Cloud Project**: You need a GCP project with Vertex AI API enabled.

## Quick Start

1.  **Install Dependencies:**
    ```bash
    make install
    ```
    This will create a virtual environment and install all required packages defined in `pyproject.toml`.

2.  **Set up credentials:**
    Ensure you have Google Cloud credentials available.
    ```bash
    gcloud auth application-default login
    ```
    Set your environment variables (create a `.env` file or export them):
    ```bash
    export GOOGLE_CLOUD_PROJECT=your-project-id
    export GOOGLE_CLOUD_LOCATION=us-central1
    # export GOOGLE_API_KEY=your-api-key # If using AI Studio instead of Vertex AI
    ```

3.  **Run Locally:**
    We provide a helper script to run all 4 agents in background processes.
    ```bash
    make run-local
    ```
    This will start:
    - Researcher (Port 8001)
    - Judge (Port 8002)
    - Content Builder (Port 8003)
    - Orchestrator (Port 8000)

4.  **Access the App:**
    Open **http://localhost:8000** in your browser. Enter a topic (e.g., "Machine Learning Basics") and watch the agents collaborate.

## Deployment

To deploy to Google Cloud Run, you need to deploy each service individually and then configure the Orchestrator with the URLs of the other services.

For detailed instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

### Summary of Deployment Steps

1.  **Deploy Leaf Agents**: Deploy `researcher`, `judge`, and `content_builder` as separate Cloud Run services.
2.  **Configure Orchestrator**: Deploy `orchestrator` and set environment variables pointing to the leaf agents:
    *   `RESEARCHER_AGENT_CARD_URL`: `https://<researcher-url>/a2a/researcher/.well-known/agent.json`
    *   `JUDGE_AGENT_CARD_URL`: `https://<judge-url>/a2a/judge/.well-known/agent.json`
    *   `CONTENT_BUILDER_AGENT_CARD_URL`: `https://<content-builder-url>/a2a/content_builder/.well-known/agent.json`
    *   `APP_URL`: `https://<orchestrator-url>`

## Developer Guide

For a deep dive into the code, architecture decisions, and how to extend the system, please refer to [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).

### Key Concepts

*   **ADK (Agent Development Kit)**: The framework used to build the agents.
*   **A2A (Agent-to-Agent)**: The protocol used for communication between the microservices.
*   **LoopAgent & SequentialAgent**: Control flow primitives used in the Orchestrator.

## Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.
