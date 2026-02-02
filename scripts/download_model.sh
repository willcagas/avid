#!/bin/bash
set -e

MODEL_DIR="$HOME/models/whisper"
MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.en.bin"
MODEL_FILE="$MODEL_DIR/ggml-medium.en.bin"

echo "Creating model directory at $MODEL_DIR..."
mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_FILE" ]; then
    echo "Model already exists at $MODEL_FILE"
    read -p "Redownload? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "Downloading Whisper medium.en model..."
curl -L -o "$MODEL_FILE" "$MODEL_URL"

echo "Download complete: $MODEL_FILE"
ls -lh "$MODEL_FILE"
