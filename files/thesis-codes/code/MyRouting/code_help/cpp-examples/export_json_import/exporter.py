#!/usr/bin/python
import json

your_dict = {
    "key1": 123,
    "key2": "hello",
    "key3": [1, 2, 3]
}
with open("data.json", "w") as f:
    json.dump(your_dict, f, indent=4)  # Indent for readability