#!/bin/bash

# Start both Bert-VITS2 and Open-LLM-VTuber servers
# This script starts Bert-VITS2 in the background and then starts Open-LLM-VTuber

# Default paths
VITS2_DIR="/home/yujin/llm_partner/Hololive-Style-Bert-VITS2"
OPEN_LLM_DIR="/home/yujin/llm_partner/Open-LLM-VTuber-1.2.1"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -v|--vits2-dir) VITS2_DIR="$2"; shift ;;
        -o|--open-llm-dir) OPEN_LLM_DIR="$2"; shift ;;
        -h|--help) echo "Usage: $0 [-v <vits2_dir>] [-o <open_llm_dir>]"; exit 0 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "🚀 Starting Bert-VITS2 and Open-LLM-VTuber..."
echo "  - VITS2 Directory: $VITS2_DIR"
echo "  - Open-LLM-VTuber Directory: $OPEN_LLM_DIR"

# Check if directories exist
if [ ! -d "$VITS2_DIR" ]; then
    echo "❌ Error: VITS2 directory not found: $VITS2_DIR"
    exit 1
fi

if [ ! -d "$OPEN_LLM_DIR" ]; then
    echo "❌ Error: Open-LLM-VTuber directory not found: $OPEN_LLM_DIR"
    exit 1
fi

# Change to Bert-VITS2 directory and start server
echo "📦 Starting Bert-VITS2 server..."
cd "$VITS2_DIR" || exit 1

# 수정: gradio_client 패치 적용
if [ -d ".venv" ]; then
    echo "🔧 Gradio Client 패치 확인 중..."
    PATCH_SCRIPT="$(dirname "$VITS2_DIR")/patch_gradio_client.py"
    if [ -f "$PATCH_SCRIPT" ]; then
        python3 "$PATCH_SCRIPT" "$(pwd)/.venv" || echo "⚠️  패치 적용 실패 (계속 진행합니다)"
    else
        echo "⚠️  패치 스크립트를 찾을 수 없습니다: $PATCH_SCRIPT"
    fi
fi

# Start Bert-VITS2 in background using uv
if [ -d ".venv" ]; then
    echo "Using .venv for Bert-VITS2"
    # 수정: .venv 환경의 python을 직접 사용하여 실행
    ./.venv/bin/python app.py --server-name 0.0.0.0 --no-autolaunch --share &
else
    echo "Using system python3 for Bert-VITS2"
    python3 app.py --server-name 0.0.0.0 --no-autolaunch --share &
fi
BERT_VITS2_PID=$!

echo "✅ Bert-VITS2 started (PID: $BERT_VITS2_PID)"
echo "⏳ Waiting 10 seconds for Bert-VITS2 to initialize..."
sleep 10

# Change to Open-LLM-VTuber directory and start server
echo "📦 Starting Open-LLM-VTuber server..."
cd "$OPEN_LLM_DIR" || exit 1

# Start Open-LLM-VTuber (this will run in foreground)
uv run python run_server.py

# When Open-LLM-VTuber stops, also stop Bert-VITS2
echo "🛑 Stopping Bert-VITS2 server..."
kill $BERT_VITS2_PID

echo "✅ Both servers stopped."
