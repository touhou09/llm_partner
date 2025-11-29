#!/usr/bin/env python3
"""Bert-VITS2 TTS 실제 호출 테스트"""

import sys
import os
import time

# Open-LLM-VTuber 경로 추가
sys.path.insert(0, '/home/yujin/llm_partner/Open-LLM-VTuber-1.2.1/src')

from open_llm_vtuber.tts.tts_factory import TTSFactory
from open_llm_vtuber.config_manager.utils import read_yaml, validate_config
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")

def test_tts():
    """TTS 엔진 테스트"""
    print("🧪 Bert-VITS2 TTS 엔진 테스트 시작...")
    
    # 수정: conf.yaml에서 설정 읽어오기
    config_path = '/home/yujin/llm_partner/Open-LLM-VTuber-1.2.1/conf.yaml'
    config_data = read_yaml(config_path)
    config = validate_config(config_data)
    tts_config = config.character_config.tts_config
    
    print(f"📋 TTS 설정 확인:")
    print(f"  model: {tts_config.tts_model}")
    if hasattr(tts_config, 'bert_vits2_tts') and tts_config.bert_vits2_tts:
        bert_config = tts_config.bert_vits2_tts
        print(f"  client_url: {bert_config.client_url}")
        print(f"  model_name: {bert_config.model_name}")
        print(f"  model_path: {bert_config.model_path}")
        print(f"  speaker: {bert_config.speaker}")
        print(f"  language: {bert_config.language}")
        print(f"  style: {bert_config.style}")
    
    # 수정: TTSFactory를 사용하여 conf.yaml의 설정으로 초기화
    tts = TTSFactory.get_tts_engine(
        tts_config.tts_model,
        **getattr(tts_config, tts_config.tts_model.lower()).model_dump(),
    )
    
    print("✅ TTS 엔진 초기화 완료")
    
    # 간단한 텍스트로 테스트
    test_text = "Hello, this is a test."
    print(f"\n📝 테스트 텍스트: '{test_text}'")
    print("🎤 오디오 생성 중...")
    
    try:
        start_time = time.time()
        audio_file = tts.generate_audio(test_text, "test_output")
        elapsed = time.time() - start_time
        
        if audio_file:
            print(f"✅ 오디오 생성 성공!")
            print(f"   파일: {audio_file}")
            print(f"   소요 시간: {elapsed:.2f}초")
            
            # 파일 존재 확인
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"   파일 크기: {file_size} bytes")
                return True
            else:
                print(f"❌ 파일이 생성되지 않았습니다: {audio_file}")
                return False
        else:
            print("❌ 오디오 생성 실패: 빈 파일 경로 반환")
            return False
            
    except Exception as e:
        print(f"❌ 오디오 생성 중 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 서버가 시작될 때까지 대기
    print("⏳ 서버 시작 대기 중...")
    time.sleep(5)
    
    success = test_tts()
    sys.exit(0 if success else 1)

