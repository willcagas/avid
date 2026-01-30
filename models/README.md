# models/

This directory is optional and can be used to store Whisper model files locally.

Alternatively, you can store models in `~/models/whisper/` as specified in the TDD.

## Downloading Models

```bash
# Option 1: Store in home directory (recommended)
mkdir -p ~/models/whisper
cd ~/models/whisper
curl -L -o ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Option 2: Store in project models/ directory
curl -L -o ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

## Available Models

| Model | Size | Notes |
|-------|------|-------|
| ggml-base.en.bin | ~142 MB | Fast, solid accuracy (recommended) |
| ggml-small.en.bin | ~466 MB | Better accuracy, slower |

Update `WHISPER_MODEL_PATH` in your `.env` file to point to the model location.
