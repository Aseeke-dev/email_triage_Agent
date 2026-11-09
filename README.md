# Personal Email Triage Agent

A Python-based assistant that helps reduce inbox overload by classifying unread emails into actionable groups and generating short, professional draft replies for urgent messages.

This project follows the challenge brief for a personal email triage agent: it reads recent unread emails, evaluates urgency, decides whether the email is urgent, follow-up, or archive material, and drafts response suggestions for the most important messages.

## Why This Project Exists

The average knowledge worker spends a significant portion of the day triaging email. A large share of that time is not spent on the actual task but on deciding:

- is this urgent?
- does it need a reply?
- can it be archived?
- what should I say if I do need to respond?

This project exists to automate that first layer of analysis so the user can focus on the emails that truly matter.

## Project Goal

Build an agent that:

1. Connects to a Gmail inbox
2. Fetches the latest unread emails
3. Classifies each email into one of three buckets:
   - `urgent`
   - `follow-up`
   - `archive`
4. Assigns an urgency score from 1 to 5
5. Drafts a two-sentence reply for urgent emails
6. Provides a simple user interface to review and copy drafts

## High-Level Workflow

The system follows a two-stage prompt workflow:

- Stage 1: Triage prompt
  - Uses sender, subject, and a short preview of the email body
  - Classifies the email and ranks urgency

- Stage 2: Drafting prompt
  - Triggered only when the message is marked urgent
  - Writes a concise, professional response based on the content

This logic is designed to keep the system lightweight, explainable, and easy to iterate during development.

## Tech Stack

- Python 3.11+
- LangChain
- Google Gemini models via `langchain-google-genai`
- Gmail API
- Streamlit
- Pydantic
- Python dotenv

## Key Features

- Gmail integration for reading unread messages
- Structured output with typed models
- Rule-based categorization with LLM reasoning
- Draft generation for urgent emails
- Mock test data for local development before live Gmail access
- Streamlit interface to review triage results.

## Project Structure

```text
email_triage_agent/
├── .env                       # Environment variables
├── .gitignore
├── .python-version
├── pyproject.toml            # Project dependencies and Python version
├── README.md                 # Project documentation
├── src/
│   └── email_triage_agent/
│       ├── agent.py          # Email triage logic
│       ├── app.py            # Streamlit user interface
│       ├── mock_data.py      # Hard-coded sample emails for testing
│       ├── prompts.py        # Prompt templates used by the agent
│       ├── schema.py         # Structured data models
│       ├── tools.py          # Gmail API interaction utilities
│       └── __init__.py
└── uv.lock                   # Dependency lock file
```

## Architecture Overview

The project is built around a simple agent pipeline:

1. Read email data
2. Preprocess the body to a short snippet
3. Pass sender, subject, and snippet to a triage prompt
4. Parse the response into a structured object
5. If the email is urgent, pass it again to a drafting prompt
6. Return the classification and optional draft reply

### 1. Email Retrieval Layer

The Gmail integration is implemented in `tools.py`.

Responsibilities:

- Authenticate with Google OAuth
- Request unread inbox messages
- Extract sender, subject, and body
- Return normalized email records for processing

### 2. Triage Layer

The logic in `agent.py` handles the classification workflow.

Responsibilities:

- Build the LLM chain
- Create a structured output object using Pydantic
- Evaluate urgency based on sender, subject, and short email preview
- Save the result per message

### 3. Drafting Layer

The drafting stage is triggered only when the outcome is `urgent`.

Responsibilities:

- Reuse the same LLM instance or a second prompt chain
- Generate a brief, professional response
- Provide a draft copy for review in the UI

### 4. User Interface Layer

The Streamlit app in `app.py` allows the user to review triage results and copy the generated response.

## Data Flow

```text
Gmail API
   ↓
Email fetcher
   ↓
Structured email objects
   ↓
Triage prompt
   ↓
Classification + urgency score
   ↓
If urgent → drafting prompt
   ↓
Draft reply
   ↓
Streamlit review panel
```

## Environment Setup

### Prerequisites

- Python 3.11 or newer
- `uv` package manager (recommended)
- Google Cloud project with Gmail API enabled
- A valid Google API credential and OAuth client
- A Gemini API key or equivalent LLM provider key

### Install Dependencies

Using `uv`:

```bash
uv sync
```

If you prefer regular pip:

```bash
pip install -r requirements.txt
```

> In this project, dependencies are managed through `pyproject.toml`, so `uv sync` is the recommended setup method.

### Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

Depending on your implementation, you may also need to configure Gmail OAuth credentials for the Google Cloud project.

## Google Gmail Setup

Before connecting to a live inbox, you must configure Gmail API access in Google Cloud Console:

1. Create a Google Cloud project
2. Enable the Gmail API
3. Create OAuth 2.0 credentials
4. Download the client secret file as `credentials.json`
5. Place it in the project root or an agreed location
6. Run the app once to complete the OAuth flow and generate `token.json`

The Gmail integration uses the read-only scope:

```python
https://www.googleapis.com/auth/gmail.readonly
```

This ensures the project can read inbox content without broad permissions.

## Local Development Strategy

The challenge statement strongly recommends starting with mock emails before connecting to Gmail. This saves time and prevents OAuth debugging from overshadowing the actual agent logic.

This repository includes mock test data in `mock_data.py`, allowing you to validate:

- prompt quality
- classification logic
- urgency scoring
- draft generation
- structured output parsing

before working with the live Gmail API.

## Prompt Design

The system uses two prompts:

### Triage Prompt

Input includes:

- sender
- subject
- email snippet

Output includes:

- category
- urgency score

The prompt instructs the assistant to classify each email into one of three buckets:

- `urgent`
- `follow-up`
- `archive`

This prompt is designed to be decisive and fast, using a short snippet rather than the entire email body to keep inference efficient.

### Drafting Prompt

The drafting prompt is triggered only when the email is marked urgent.

This prompt should:

- be brief
- sound professional
- produce exactly two sentences
- avoid greetings and sign-offs
- reflect a concise executive tone

The challenge statement also suggests using a few past email examples as style references so the generated response matches the user’s communication style.

## Structured Output

The project uses Pydantic models to ensure that the LLM response is well-formed and predictable.

A typical output looks like this:

```json
{
  "category": "urgent",
  "urgency_score": 5,
  "draft_reply": "I can review this by end of day. Please send the latest figures and I will respond with a final update."
}
```

The benefit of structured output is that downstream logic can safely consume the result without parsing freeform text.

## Running the Project

### 1. Run the sandbox test

This is the recommended development step before live inbox integration:

```bash
uv run python src/email_triage_agent/agent.py
```

This executes the mock email path and validates the triage and draft flow.

### 2. Run the Streamlit app

```bash
uv run streamlit run src/email_triage_agent/app.py
```

The app lets the user:

- review each classified email
- inspect urgency score
- copy the drafted reply
- decide whether to send or edit it

## Example Workflow

A sample email may look like this:

- Sender: finance@company.com
- Subject: Q3 financial report needed by EOD
- Body: urgent request for final numbers before close of business

The triage model may classify it as:

```json
{
  "category": "urgent",
  "urgency_score": 5
}
```

Then the drafting model may create:

> I can review the report before end of day. Please send the latest figures and I’ll return a final update immediately.

## Current Limitations

This project is a strong first-pass prototype, but it has some practical limitations:

- It reads only unread inbox messages
- It does not yet support thread-aware context or full email history
- The Gmail API setup requires OAuth configuration
- The model output depends on the chosen LLM provider and prompt quality
- The urgency classification is heuristic and may vary based on prompt design
- Drafting is still a suggestion and should be reviewed before sending

## Future Enhancements

Potential next steps for a production-ready version include:

- Connect to the full Gmail API with filters and labels
- Support user preferences and custom reply tone
- Add memory or style references from past emails
- Add a human-in-the-loop review step before sending
- Support multiple inboxes or shared team inboxes
- Add logging, evaluation metrics, and test coverage
- Integrate with LangGraph for more structured workflows

## Best Practices Learned

This project teaches several important engineering patterns:

- Tool calling with external APIs
- Structured output parsing for reliable downstream processing
- Few-shot prompting using sample emails
- Separation of triage and drafting concerns
- Local prototyping with mock data before production integration

## Success Criteria

The project is considered successful when:

- unread emails are fetched successfully
- each email is classified into the expected category
- urgent emails receive a useful draft response
- the interface is easy to use and review
- the workflow is fast enough for a daily productivity use case

## Summary

This project is a practical AI productivity assistant that reduces inbox overhead by automating the time-consuming first pass of email triage. It takes the manual burden of reading, prioritizing, and drafting responses and turns it into a repeatable workflow powered by LLMs and Gmail integration.

It is a strong example of applying modern AI tooling to a real-world productivity problem while keeping the implementation approachable for a learning project or prototype.

## License

This project is intended for educational and personal productivity use. Add a license if you plan to share or distribute the repository publicly.

## Acknowledgements

This project was inspired by the challenge requirement for a personal email triage agent and by practical LangChain workflows for working with AI agents, tools, and structured output.
