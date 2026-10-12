# Data Platform

An end-to-end Data Engineering project built step by step.

## Setup

    py -3.11 -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    pip install -e .

## Run tests

    pytest



## Database

    docker compose up -d
    python -m data_platform

## Windows note

If a compiled package fails with "Application Control policy has blocked
this file", install an older release of that package.