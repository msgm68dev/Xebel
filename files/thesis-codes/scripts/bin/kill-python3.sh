#!/bin/bash

ps aux | grep python3 | awk '{print $2}' | xargs -Ip kill -9 p
