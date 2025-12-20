#!/usr/bin/env python3
"""Test language detection and per-language TTS settings."""

import sys
sys.path.insert(0, '/home/yujin/llm_partner/Open-LLM-VTuber-1.2.1/src')

from open_llm_vtuber.tts.bert_vits2_tts import TTSEngine, detect_language

# Test language detection
print("=" * 50)
print("Testing Language Detection")
print("=" * 50)

test_texts = [
    ("Hello, how are you today?", "EN"),
    ("こんにちは、元気ですか？", "JP"),
    ("今日は天気がいいですね", "JP"),
    ("The weather is nice today", "EN"),
    ("私はアメリアです", "JP"),
    ("I love programming", "EN"),
    ("東京タワー", "JP"),
]

for text, expected in test_texts:
    detected = detect_language(text)
    status = "✅" if detected == expected else "❌"
    print(f"{status} '{text[:30]}...' -> {detected} (expected: {expected})")

# Test TTS with per-language settings
print("\n" + "=" * 50)
print("Testing TTS with Per-Language Settings")
print("=" * 50)

tts = TTSEngine(
    client_url="http://127.0.0.1:7860",
    auto_detect_language=True,
    default_language="EN",
    en={
        "model_name": "SBV2_HoloHi",
        "model_path": "/home/yujin/llm_partner/Hololive-Style-Bert-VITS2/model_assets/SBV2_HoloHi/SBV2_HoloHi.safetensors",
        "speaker": "AmeliaWatson",
        "style": "Amelia",
        "style_weight": 3.0,
    },
    jp={
        "model_name": "SBV2_HoloJPTest3",
        "model_path": "/home/yujin/llm_partner/Hololive-Style-Bert-VITS2/model_assets/SBV2_HoloJPTest3/SBV2_HoloJPTest3.safetensors",
        "speaker": "ShirakamiFubuki",
        "style": "Neutral",
        "style_weight": 3.0,
    },
)

# Test English TTS
print("\n🇺🇸 Testing English TTS...")
try:
    en_result = tts.generate_audio("Hello! This is a test of English text to speech.")
    if en_result:
        print(f"   ✅ English audio generated: {en_result}")
    else:
        print("   ❌ English audio generation failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Japanese TTS
print("\n🇯🇵 Testing Japanese TTS...")
try:
    jp_result = tts.generate_audio("こんにちは！これは日本語のテストです。")
    if jp_result:
        print(f"   ✅ Japanese audio generated: {jp_result}")
    else:
        print("   ❌ Japanese audio generation failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)
