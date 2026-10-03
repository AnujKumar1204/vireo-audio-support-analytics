# vireo-audio-support-analytics
AI-assisted support analytics dashboard for Vireo Audio, providing weekly complaint insights and agent ticket-closure leaderboards.
# Vireo Audio Support Analytics

AI-assisted support analytics tool for Vireo Audio.

## What it does

- Shows weekly customer complaint categories and counts.
- Shows weekly agent ticket-closure leaderboard.
- Uses an LLM to reclassify tickets originally marked as "Other".
- Saves completed AI classifications in `labels.csv`.

## Setup

1. Install Python.
2. Install dependencies:

```bash
pip install -r requirements.txt
