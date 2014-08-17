# GradientBot

This bot uses a gradient heuristic based on the map and the map objects to make the best decision.

## Usage

Run with:

	python client.py mySecretKey arena 10

When run, it will open a chrome browser with a display of the bot's internal heuristics.

## Setup 

Should work with python2 and python3.

Install deps:

    pip install -r requirements.txt

Run with:

    python client.py <key> <[training|arena]> <number-of-games-to-play> [server-url]

Examples:

    python client.py mySecretKey arena 10
    python client.py mySecretKey training 10 http://localhost:9000
