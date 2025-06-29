# 🌀 Agentic Randomness – Product Requirements Document (PRD)

## Overview

**Agentic Randomness** is a personal AI agent, which we'll personify as "Randy", that introduces spontaneity and novelty into daily life by proactively suggesting interesting activities. It’s designed to operate autonomously, within user-defined boundaries, and aims to make life feel more dynamic and less predictable.

This project is part technical exploration (into agentic workflows and autonomy) and part personal assistant for enhancing everyday living.

---

## Goals

- Encourage spontaneity and discovery by surfacing random but relevant activity suggestions.
- Learn by building: gain hands-on experience with autonomous AI agents and scheduling logic in Python.
- Keep the system simple, extensible, and flexible for future integrations.

---

## Core Features (v1)

### 1. Proactive Recommendation Cadence

- The agent will autonomously send **one suggestion per week** (or based on a configurable interval).
- Suggestions must respect **quiet hours** (e.g., no messages between 11:00 PM – 7:00 AM).

### 2. Suggestion Domains

The agent will randomly choose a domain each time it decides to make a suggestion:

- **Restaurants**: Local dining recommendations.
- **Points of Interest**: Parks, museums, outdoor locations, etc.
- **Movies**: Random watch suggestions, independent of location.

Each output will be a brief, friendly message including the recommendation and a short reason or comment.

### 3. Region Awareness

- Agent will use a **static region input** (e.g., Charleston, SC) for generating local suggestions.

### 4. Delivery Method

- **Primary:** Email (SMTP or transactional email provider).
- **Secondary (future):** SMS/text message.

### 5. Autonomy & Timing

- Agent decides **when** to send the weekly recommendation.
- Autonomy is limited by:
  - Cadence control (max 1 per time window).
  - Quiet hour exclusion window.

### 5. Memory

- Agent will leverage memory to keep a history of previous recommendations as to not recommend the same thing twice

---

## Nice-to-Haves (Future Iterations)

- Weather-aware filtering to avoid recommending outdoor activities during storms.
- “Go deeper” option to allow the user to request follow-up ideas or variations.
- Opt-in user preferences (e.g., vegetarian, types of activities, preferred movie genres).
- SMS-based confirmations or chat-based interactions.
- More suggestion types (books, TV shows, short road trips, events).
- Human feedback learning extension to memory. Allow the user to rate the recomennded experience and/or provide feedback as to whether they ended up taking action on the recommendation. This feedback can be used to help refine and improve future recommendations by the agent.

---

## Tone & Personality

- Suggestions should sound **friendly, casual, and engaging**.
  - _Example:_ “Hey! Feeling adventurous? There’s a cozy Thai spot downtown that might be perfect tonight 🌶️”

---

## Constraints

- No front-end needed for v1, although keeping logs within the program so that the operator (me, Nick Markman), can inspect and review over time to help with future refinements
- Do not exceed the configured cadence (1x per week max).
- Avoid complex dependencies up front. Work iteratively to get a simple proof of concept out, which we can improve and extend features to over time
- Agent should be built in Python and structured for extensibility.

---

## Out of Scope (for now)

- Multi-user support.
- Deep user personalization or profiles.
- Full weather or calendar syncing.
- Slack or other messaging platforms.