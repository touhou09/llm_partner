#!/usr/bin/env python3
"""Bert-VITS2 TTS 연결 테스트 스크립트"""

import sys
import os
sys.path.insert(0, '/home/yujin/llm_partner/Open-LLM-VTuber-1.2.1/src')

from gradio_client import Client
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")

def test_connection():
    """Bert-VITS2 서버 연결 테스트"""
    client_url = "http://127.0.0.1:7860"
    
    print(f"🔍 Testing connection to {client_url}...")
    
    try:
        # Client 초기화
        client = Client(client_url, max_workers=1)
        print("✅ Client initialized successfully")
        
        # API 정보 확인
        if hasattr(client, 'endpoints'):
            print(f"📋 Found {len(client.endpoints)} endpoints")
            for i, endpoint in enumerate(client.endpoints):
                if hasattr(endpoint, 'protocol'):
                    print(f"  Endpoint {i}: protocol={endpoint.protocol}")
                if hasattr(endpoint, 'api_name'):
                    print(f"  Endpoint {i}: api_name={endpoint.api_name}")
        
        # 간단한 predict 테스트 (fn_index=16 사용)
        print("\n🧪 Testing predict() with fn_index=16...")
        print("   (This may take a moment...)")
        
        # 최소한의 파라미터로 테스트
        result = client.predict(
            "",  # model_name
            "",  # model_path
            "test",  # text
            "EN",  # language
            None,  # reference_audio_path
            0.2,  # sdp_ratio
            0.6,  # noise_scale
            0.8,  # noise_scale_w
            1.0,  # length_scale
            True,  # line_split
            0.5,  # split_interval
            "",  # assist_text
            0.7,  # assist_text_weight
            False,  # use_assist_text
            "Neutral",  # style
            3.0,  # style_weight
            "",  # kata_tone_json_str
            False,  # use_tone
            "",  # speaker
            fn_index=16,
        )
        
        print(f"✅ Predict successful! Result type: {type(result)}")
        if result:
            print(f"   Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        
        if "403" in error_msg or "WebSocket" in error_msg:
            print("\n⚠️  WebSocket 403 error detected!")
            print("   This indicates the server is rejecting WebSocket connections.")
            print("   The client is trying to use WebSocket but the server doesn't allow it.")
        
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

