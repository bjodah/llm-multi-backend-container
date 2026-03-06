#!/bin/bash
curl -s -X POST http://127.0.0.1:8686/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{
    "model": "FLUX.2-klein-4B",
    "prompt": "A futuristic city skyline at sunset in a cyberpunk style",
    "size": "1024x1024",
    "num_inference_steps": 20,
    "response_format": "b64_json"
  }' | jq -r '.data[0].b64_json' | base64 --decode > generated_image.png
