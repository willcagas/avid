#!/bin/bash
set -e

MODEL_DIR="$HOME/models/whisper"
INPUT_MODEL="$MODEL_DIR/ggml-medium.en.bin"
OUTPUT_MODEL="$MODEL_DIR/ggml-medium.en-q5_0.bin"
QUANTIZE_BIN="whisper-quantize"

if [ ! -f "$INPUT_MODEL" ]; then
    echo "Error: Input model not found at $INPUT_MODEL"
    exit 1
fi

if [ -f "$OUTPUT_MODEL" ]; then
    echo "Output model already exists at $OUTPUT_MODEL"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "Quantizing model to q5_0..."
"$QUANTIZE_BIN" "$INPUT_MODEL" "$OUTPUT_MODEL" q5_0

echo "Quantization complete: $OUTPUT_MODEL"
ls -lh "$OUTPUT_MODEL"
