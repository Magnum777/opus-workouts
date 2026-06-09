#!/usr/bin/env python3
"""Transcribe audio/video files using Faster-Whisper (local, free).
Usage: python transcribe.py <audio_or_video_file> [--model base|small|medium|large]
"""
import sys, os, argparse

sys.stdout.reconfigure(encoding="utf-8")


def transcribe_file(path, model_size="base"):
    from faster_whisper import WhisperModel

    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    print(f"Loading model '{model_size}' (first run downloads ~150MB–5GB)...")
    # Use CPU int8 for speed + no GPU dependency; change to "float16" + device="cuda" for GPU
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Transcribing: {path}")
    segments, info = model.transcribe(path, beam_size=5, vad_filter=True)

    print(f"\nDetected language: {info.language} (probability {info.language_probability:.2%})")
    print(f"Duration: {info.duration:.1f}s\n")
    print("=" * 60)

    full_text = []
    for seg in segments:
        line = f"[{seg.start:.2f} → {seg.end:.2f}] {seg.text}"
        print(line)
        full_text.append(line)

    # Save to .txt alongside the input file
    out = os.path.splitext(path)[0] + ".txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"File: {path}\nLanguage: {info.language}\nDuration: {info.duration:.1f}s\n\n")
        f.write("\n".join(full_text))
    print(f"\nSaved to: {out}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Transcribe audio with Faster-Whisper")
    ap.add_argument("file", help="Audio or video file path")
    ap.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
                    help="Model size (default: base). Larger = more accurate, slower")
    args = ap.parse_args()
    transcribe_file(args.file, args.model)
