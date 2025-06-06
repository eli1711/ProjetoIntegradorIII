#!/usr/bin/env bash
rasa run actions &
rasa run --enable-api --cors '*' --debug