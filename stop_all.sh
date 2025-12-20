#!/bin/bash

# 모든 Bert-VITS2 및 Open-LLM-VTuber 관련 프로세스를 종료하는 스크립트

echo "🛑 모든 관련 프로세스를 종료하는 중..."

# 1. app.py 프로세스 종료
echo "📦 Bert-VITS2 서버 종료 중..."
pkill -f "app.py" 2>/dev/null

# 2. run_server.py 프로세스 종료
echo "📦 Open-LLM-VTuber 서버 종료 중..."
pkill -f "run_server.py" 2>/dev/null

# 3. uvicorn 프로세스 종료
echo "📦 Uvicorn 서버 종료 중..."
pkill -f "uvicorn" 2>/dev/null

# 4. Gradio frpc 프로세스 종료
echo "📦 Gradio 터널링 프로세스 종료 중..."
pkill -f "frpc_linux_amd64" 2>/dev/null

# 5. 포트 사용 프로세스 강제 종료
echo "🔌 포트 해제 중..."
fuser -k 7860/tcp 7861/tcp 12393/tcp 2>/dev/null
lsof -ti :7860,:7861,:12393 2>/dev/null | xargs kill -9 2>/dev/null

# 6. 남은 프로세스 강제 종료
sleep 1
REMAINING=$(ps aux | grep -E "(app\.py|run_server\.py|uvicorn|gradio|frpc)" | grep -v grep)
if [ -n "$REMAINING" ]; then
    echo "⚠️  남은 프로세스 강제 종료 중..."
    pkill -9 -f "app.py" 2>/dev/null
    pkill -9 -f "run_server.py" 2>/dev/null
    pkill -9 -f "uvicorn" 2>/dev/null
    pkill -9 -f "frpc_linux_amd64" 2>/dev/null
fi

# 7. 최종 확인
sleep 1
REMAINING=$(ps aux | grep -E "(app\.py|run_server\.py|uvicorn|gradio|frpc|7860|7861|12393)" | grep -v grep)
if [ -z "$REMAINING" ]; then
    echo "✅ 모든 관련 프로세스가 종료되었습니다."
else
    echo "⚠️  다음 프로세스가 아직 실행 중입니다:"
    echo "$REMAINING"
    echo ""
    echo "강제 종료하려면 다음 명령을 실행하세요:"
    echo "  pkill -9 -f 'app.py'"
    echo "  pkill -9 -f 'run_server.py'"
    echo "  pkill -9 -f 'frpc_linux_amd64'"
fi

