# PantryPilot

**AI-powered pantry management and meal suggestions to reduce food waste.**

PantryPilot helps users manage pantry ingredients, monitor expiry dates, and discover meal ideas using the ingredients they already have. It integrates **Lyzr AI, Qdrant vector memory, and Omi voice input** to make meal planning more convenient.
## 🚀 Live Demo

**Try PantryPilot:** https://reduces-cam-promotional-manga.trycloudflare.com

*Note: This temporary demo link works only while the server and tunnel are running.*

## Features

- **Pantry Management:** Add and manage available ingredients.
- **Expiry Tracking:** Identify ingredients that should be used soon.
- **AI Meal Suggestions:** Generate recipe ideas based on available ingredients.
- **Omi Voice Integration:** Request meal suggestions through voice transcripts.
- **Persistent Memory:** Use Qdrant to store and retrieve relevant context.
- **AI Orchestration:** Integrate Lyzr for AI-powered meal suggestions.

## Technology Stack

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **AI Orchestration:** Lyzr
- **Vector Memory:** Qdrant
- **Voice Input:** Omi

## How the Integrations Work

- **Omi:** Sends conversation transcript segments to PantryPilot through a webhook.
- **Qdrant:** Provides vector-based memory for storing and retrieving relevant information.
- **Lyzr:** Supports AI-powered recipe generation.

## Running Locally

1. Install Python and the required dependencies.
2. Configure the necessary API credentials in a local `.env` file.
3. Start the FastAPI application.
4. Open the local website in your browser.

Keep `.env`, API keys, and personal pantry data private. Do not commit secrets to GitHub.

## Project Goal

PantryPilot aims to make everyday meal planning easier while encouraging users to use ingredients before they expire and reduce avoidable food waste.
