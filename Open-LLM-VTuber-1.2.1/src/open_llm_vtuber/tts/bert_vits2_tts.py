"""
Bert-VITS2 TTS Engine for Open-LLM-VTuber.

This module provides integration with Hololive-Style-Bert-VITS2 via Gradio Client API.
"""

import os
import re
import json
import base64
from pathlib import Path
from typing import Optional

import httpx
import numpy as np
from gradio_client import Client
from loguru import logger

from .tts_interface import TTSInterface


class TTSEngine(TTSInterface):
    """Bert-VITS2 TTS Engine using Gradio Client."""

    def __init__(
        self,
        client_url: str = "http://127.0.0.1:7860",
        model_name: str = "",
        model_path: str = "",
        speaker: str = "",
        language: str = "EN",
        style: str = "Neutral",
        style_weight: float = 3.0,
        sdp_ratio: float = 0.2,
        noise_scale: float = 0.6,
        noise_scale_w: float = 0.8,
        length_scale: float = 1.0,
        line_split: bool = True,
        split_interval: float = 0.5,
        use_style_text: bool = False,
        style_text: str = "",
        style_text_weight: float = 0.7,
        reference_audio_path: Optional[str] = None,
    ):
        """
        Initialize Bert-VITS2 TTS Engine.

        Args:
            client_url: URL of the Bert-VITS2 Gradio server
            model_name: Model name (e.g., 'mori')
            model_path: Path to model file
            speaker: Speaker ID
            language: Language code (EN, JP, ZH)
            style: Style preset name (e.g., 'Neutral')
            style_weight: Style intensity (0-20)
            sdp_ratio: SDP ratio (0-1)
            noise_scale: Noise scale (0.1-2)
            noise_scale_w: Noise scale W (0.1-2)
            length_scale: Length scale (0.1-2)
            line_split: Whether to split by line breaks
            split_interval: Interval between splits in seconds
            use_style_text: Whether to use style text
            style_text: Text for style guidance
            style_text_weight: Style text weight (0-1)
            reference_audio_path: Path to reference audio for style
        """
        self.client_url = client_url
        self.model_name = model_name
        # 수정: model_path 처리 - conf.yaml에서 절대 경로나 상대 경로 모두 사용 가능
        # 절대 경로는 그대로 사용, 상대 경로는 Open-LLM-VTuber-1.2.1 디렉토리 기준으로 절대 경로로 변환
        if model_path:
            if os.path.isabs(model_path):
                self.model_path = model_path
            else:
                # 상대 경로인 경우 Open-LLM-VTuber-1.2.1 디렉토리 기준으로 절대 경로로 변환
                # conf.yaml이 Open-LLM-VTuber-1.2.1 디렉토리에 있으므로 그 기준으로 해석
                base_dir = Path(__file__).parent.parent.parent.parent  # Open-LLM-VTuber-1.2.1 디렉토리
                self.model_path = str((base_dir / model_path).resolve())
        else:
            self.model_path = model_path
        self.speaker = speaker
        self.language = language
        self.style = style
        self.style_weight = style_weight
        self.sdp_ratio = sdp_ratio
        self.noise_scale = noise_scale
        self.noise_scale_w = noise_scale_w
        self.length_scale = length_scale
        self.line_split = line_split
        self.split_interval = split_interval
        self.use_style_text = use_style_text
        self.style_text = style_text
        self.style_text_weight = style_text_weight
        self.reference_audio_path = reference_audio_path

        self.client: Optional[Client] = None
        # 수정: output_dir을 클래스 변수로 관리하여 재사용
        self._output_dir: Optional[str] = None
        # 수정: HTTP 클라이언트 추가 (WebSocket 우회용)
        self._http_client: Optional[httpx.Client] = None
        self._api_info: Optional[dict] = None
        logger.info(f"🎤 Initialized Bert-VITS2 TTS Engine at {client_url}")

    def _get_api_info(self) -> dict:
        """수정: gradio_client를 사용하여 API 정보 가져오기 (초기화된 client 활용)"""
        if self._api_info is None:
            try:
                # gradio_client가 이미 API 정보를 가지고 있으므로 활용
                client = self._get_client()
                
                # gradio_client의 내부 API 정보 가져오기
                if hasattr(client, 'api_info'):
                    self._api_info = client.api_info
                elif hasattr(client, 'config'):
                    # config에서 API 정보 추출
                    self._api_info = client.config
                else:
                    # 직접 HTML에서 API 정보 파싱
                    if self._http_client is None:
                        self._http_client = httpx.Client(timeout=30.0)
                    
                    response = self._http_client.get(self.client_url)
                    response.raise_for_status()
                    html = response.text
                    
                    # JavaScript 변수에서 API 정보 추출 시도
                    import re
                    # window.gradio_config 또는 유사한 패턴 찾기
                    # 간단하게 gradio_client를 통해 가져오기
                    logger.warning("⚠️  API info not found in client, using gradio_client's internal method")
                    # gradio_client가 이미 초기화되어 있으므로 그대로 사용
                    self._api_info = {}
                
                logger.info(f"✅ API info retrieved successfully")
            except Exception as e:
                logger.error(f"❌ Failed to get API info: {e}")
                # API 정보가 없어도 계속 진행 (gradio_client가 처리)
                self._api_info = {}
        return self._api_info
    
    def _predict_via_http(self, fn_index: int, data: list) -> tuple:
        """수정: requests를 사용하여 직접 HTTP API 호출 (WebSocket 완전 우회, gradio_client와 동일한 형식)"""
        import time
        import uuid
        import requests  # 수정: httpx 대신 requests 사용 (gradio_client와 동일)
        import json as json_module
        
        try:
            # 수정: gradio_client와 동일한 형식으로 요청 구성
            base_url = self.client_url.rstrip('/')
            predict_url = f"{base_url}/api/predict/"
            
            # 세션 해시 생성 (gradio_client의 session_hash 사용)
            session_hash = self.client.session_hash if hasattr(self.client, 'session_hash') else str(uuid.uuid4())
            
            # 수정: Gradio의 /api/predict/ API 형식에 맞게 요청 구성
            # gradio_client는 json.dumps() 후 data=로 전송함 (requests.post의 data= 파라미터 사용)
            payload_dict = {
                "data": data,
                "fn_index": fn_index,
                "session_hash": session_hash,
            }
            payload_str = json_module.dumps(payload_dict)
            
            logger.info(f"📤 Sending HTTP POST to {predict_url} (fn_index={fn_index})...")
            logger.debug(f"📤 Payload keys: {list(payload_dict.keys())}, data length: {len(data)}")
            logger.debug(f"📤 model_name: {data[0] if len(data) > 0 else 'N/A'}, speaker: {data[-1] if len(data) > 0 else 'N/A'}")
            
            # 수정: gradio_client와 동일한 형식으로 전송 (json.dumps() 후 data=로 전송)
            # gradio_client의 make_predict에서는 requests.post(api_url, headers=headers, data=data) 형식 사용
            headers = dict(self.client.headers) if hasattr(self.client, 'headers') else {}
            response = requests.post(predict_url, headers=headers, data=payload_str, timeout=300.0)
            
            # 수정: 500 에러 발생 시 응답 본문 확인 및 상세 로깅
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"❌ HTTP request failed with status {response.status_code}: {error_detail}")
                logger.debug(f"📤 Request payload (first 3 items): {data[:3] if len(data) >= 3 else data}")
                response.raise_for_status()
            
            result_data = response.json()
            
            # 수정: Gradio의 /api/predict/ 응답 형식 처리
            # 응답 형식: {"data": [...]} (동기) 또는 {"hash": "...", "queue": true} (비동기)
            if "data" in result_data:
                # 동기 응답인 경우
                result = result_data["data"]
            elif "hash" in result_data:
                # 비동기 작업인 경우 - 해시로 결과 폴링
                job_hash = result_data["hash"]
                logger.info(f"⏳ Polling for result (hash: {job_hash[:8]}...)...")
                
                # 결과 폴링 (최대 5분 대기)
                max_wait_time = 300
                poll_interval = 0.5
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    time.sleep(poll_interval)
                    
                    # 수정: 상태 확인 - /api/queue/status 경로 사용
                    status_url = f"{base_url}/api/queue/status"
                    status_payload = {"hash": job_hash}
                    status_response = self._http_client.post(status_url, json=status_payload)
                    status_response.raise_for_status()
                    status_data = status_response.json()
                    
                    if status_data.get("status") == "COMPLETE":
                        # 결과 가져오기
                        result_url = f"{base_url}/api/queue/result"
                        result_response = self._http_client.post(result_url, json={"hash": job_hash})
                        result_response.raise_for_status()
                        result_data = result_response.json()
                        result = result_data.get("data", [])
                        break
                    elif status_data.get("status") == "FAILED":
                        error_msg = status_data.get("error", "Unknown error")
                        logger.error(f"❌ Job failed: {error_msg}")
                        raise Exception(f"TTS job failed: {error_msg}")
                else:
                    raise Exception("TTS job timed out")
            elif "event_id" in result_data:
                # 수정: event_id를 사용하여 결과 폴링 (Gradio의 최신 형식)
                event_id = result_data["event_id"]
                logger.info(f"⏳ Polling for result (event_id: {event_id[:8]}...)...")
                
                # 결과 폴링 (최대 5분 대기)
                max_wait_time = 300
                poll_interval = 0.5
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    time.sleep(poll_interval)
                    
                    # 수정: 상태 확인 (event_id 사용) - /queue/status 경로 사용
                    status_url = f"{base_url}/queue/status"
                    status_payload = {"event_id": event_id}
                    status_response = requests.post(status_url, headers=headers, json=status_payload, timeout=300.0)
                    status_response.raise_for_status()
                    status_data = status_response.json()
                    
                    if status_data.get("status") == "COMPLETE":
                        # 결과 가져오기
                        result_url = f"{base_url}/queue/result"
                        result_response = requests.post(result_url, headers=headers, json={"event_id": event_id}, timeout=300.0)
                        result_response.raise_for_status()
                        result_data = result_response.json()
                        result = result_data.get("data", [])
                        break
                    elif status_data.get("status") == "FAILED":
                        error_msg = status_data.get("error", "Unknown error")
                        logger.error(f"❌ Job failed: {error_msg}")
                        raise Exception(f"TTS job failed: {error_msg}")
                else:
                    raise Exception("TTS job timed out")
            elif "hash" in result_data:
                # 비동기 작업인 경우 - 해시로 결과 폴링 (구버전 형식)
                job_hash = result_data["hash"]
                logger.info(f"⏳ Polling for result (hash: {job_hash[:8]}...)...")
                
                # 결과 폴링 (최대 5분 대기)
                max_wait_time = 300
                poll_interval = 0.5
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    time.sleep(poll_interval)
                    
                    # 수정: 상태 확인 - /api/queue/status 경로 사용
                    status_url = f"{base_url}/api/queue/status"
                    status_payload = {"hash": job_hash}
                    status_response = http_client.post(status_url, json=status_payload)
                    status_response.raise_for_status()
                    status_data = status_response.json()
                    
                    if status_data.get("status") == "COMPLETE":
                        # 결과 가져오기
                        result_url = f"{base_url}/api/queue/result"
                        result_response = http_client.post(result_url, json={"hash": job_hash})
                        result_response.raise_for_status()
                        result_data = result_response.json()
                        result = result_data.get("data", [])
                        break
                    elif status_data.get("status") == "FAILED":
                        error_msg = status_data.get("error", "Unknown error")
                        logger.error(f"❌ Job failed: {error_msg}")
                        raise Exception(f"TTS job failed: {error_msg}")
                else:
                    raise Exception("TTS job timed out")
            else:
                logger.error(f"❌ Unexpected response format: {result_data}")
                raise Exception(f"Unexpected API response: {result_data}")
            
            # 결과 파싱
            if not isinstance(result, (list, tuple)) or len(result) < 2:
                logger.error(f"❌ Unexpected result format: {type(result)}, value: {result}")
                raise Exception(f"Unexpected result format: {result}")
            
            message = result[0] if result[0] is not None else ""
            audio_data = result[1]
            kata_tone = result[2] if len(result) > 2 else ""
            
            if audio_data is None:
                logger.error(f"❌ TTS generation failed: {message}")
                raise Exception(f"TTS generation failed: {message}")
            
            # audio_data는 파일 경로 문자열 또는 딕셔너리일 수 있음
            if isinstance(audio_data, dict):
                # Gradio의 FileData 형식: {"path": "...", "url": "...", ...}
                # 수정: url 필드를 우선 사용 (Gradio가 제공하는 완전한 URL)
                audio_url = audio_data.get("url")
                if not audio_url:
                    # url이 없으면 path를 사용하여 URL 구성
                    audio_path = audio_data.get("path")
                    if not audio_path:
                        raise Exception(f"Invalid audio data format: {audio_data}")
                    if audio_path.startswith("http://") or audio_path.startswith("https://"):
                        audio_url = audio_path
                    elif audio_path.startswith("/"):
                        audio_url = f"{self.client_url}{audio_path}"
                    else:
                        audio_url = f"{self.client_url}/file={audio_path}"
            elif isinstance(audio_data, str):
                # 문자열인 경우 URL로 변환
                audio_path = audio_data
                if audio_path.startswith("http://") or audio_path.startswith("https://"):
                    audio_url = audio_path
                elif audio_path.startswith("/"):
                    audio_url = f"{self.client_url}{audio_path}"
                else:
                    audio_url = f"{self.client_url}/file={audio_path}"
            else:
                raise Exception(f"Unexpected audio data type: {type(audio_data)}")
            
            logger.debug(f"📥 Downloading audio from {audio_url}")
            # 수정: requests 사용 (httpx 대신)
            import requests
            headers = dict(self.client.headers) if hasattr(self.client, 'headers') else {}
            audio_response = requests.get(audio_url, headers=headers, timeout=300.0)
            audio_response.raise_for_status()
            
            # WAV 파일을 읽어서 numpy 배열로 변환
            import io
            import scipy.io.wavfile as wavfile
            audio_bytes = io.BytesIO(audio_response.content)
            sample_rate, audio_array = wavfile.read(audio_bytes)
            audio_tuple = (sample_rate, audio_array)
            
            logger.info(f"✅ Audio downloaded: {sample_rate}Hz, {len(audio_array)} samples")
            return message, audio_tuple, kata_tone
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ HTTP predict failed: {error_msg}")
            raise

    def _get_client(self) -> Client:
        """Get or create Gradio client."""
        if self.client is None:
            try:
                # 수정: WebSocket 연결 문제 해결을 위해 output_dir 옵션 추가
                # output_dir을 지정하면 WebSocket 대신 HTTP를 사용할 수 있음
                if self._output_dir is None:
                    import tempfile
                    self._output_dir = tempfile.mkdtemp(prefix="bert_vits2_")
                
                # 수정: Client 초기화 (기본 설정)
                self.client = Client(
                    self.client_url,
                    max_workers=1,  # 동시 연결 제한
                )
                
                # 수정: WebSocket 403 에러 해결을 위해 모든 endpoint의 use_ws를 False로 설정
                # HTTP만 사용하도록 강제
                if hasattr(self.client, 'endpoints') and self.client.endpoints:
                    for endpoint in self.client.endpoints:
                        if hasattr(endpoint, 'use_ws'):
                            endpoint.use_ws = False
                            logger.debug(f"✅ Disabled WebSocket for endpoint {getattr(endpoint, 'fn_index', 'unknown')}")
                        # protocol 속성도 확인 및 수정
                        if hasattr(endpoint, 'protocol'):
                            original_protocol = endpoint.protocol
                            # HTTP 모드에서는 "sse" 프로토콜 사용 (Gradio의 HTTP API는 SSE 사용)
                            # "http"가 아닌 "sse"를 사용해야 함
                            if original_protocol not in ("sse", "sse_v1", "sse_v2", "sse_v2.1", "sse_v3"):
                                endpoint.protocol = "sse"  # HTTP 모드에서는 SSE 사용
                                logger.debug(f"✅ Set protocol to SSE for endpoint {getattr(endpoint, 'fn_index', 'unknown')} (was {original_protocol})")
                    
                    # 수정: make_predict를 다시 호출하여 use_ws 변경사항 반영
                    # make_predict는 use_ws 값을 확인하여 _ws_fn 또는 HTTP 요청을 선택함
                    for endpoint in self.client.endpoints:
                        if hasattr(endpoint, 'make_predict'):
                            # make_predict를 다시 호출하여 use_ws=False 반영
                            try:
                                # 기존 predict 함수를 무효화하고 다시 생성
                                if hasattr(endpoint, 'predict'):
                                    delattr(endpoint, 'predict')
                                logger.debug(f"✅ Reset predict function for endpoint {getattr(endpoint, 'fn_index', 'unknown')}")
                            except Exception as e:
                                logger.debug(f"⚠️  Could not reset predict function: {e}")
                    
                    logger.info(f"✅ Disabled WebSocket for all endpoints, using HTTP only")
                
                logger.info(f"✅ Connected to Bert-VITS2 server at {self.client_url}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Failed to connect to Bert-VITS2 server: {e}")
                
                # 수정: WebSocket 403 에러 발생 시 output_dir 재생성 후 재시도
                if "403" in error_msg or "WebSocket" in error_msg or "rejected" in error_msg:
                    try:
                        logger.warning("⚠️  WebSocket connection rejected, retrying with new output_dir...")
                        import tempfile
                        import shutil
                        # 기존 output_dir 정리
                        if self._output_dir and os.path.exists(self._output_dir):
                            try:
                                shutil.rmtree(self._output_dir)
                            except Exception:
                                pass
                        self._output_dir = tempfile.mkdtemp(prefix="bert_vits2_")
                        
                        # 재시도 시에도 동일한 헤더 설정 적용
                        self.client = Client(
                            self.client_url,
                            max_workers=1,
                        )
                        
                        # 헤더 추가
                        from urllib.parse import urlparse
                        parsed_url = urlparse(self.client_url)
                        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
                        if hasattr(self.client, 'headers'):
                            if isinstance(self.client.headers, dict):
                                self.client.headers["Origin"] = origin
                                self.client.headers["User-Agent"] = "gradio-client"
                            elif hasattr(self.client.headers, 'update'):
                                self.client.headers.update({"Origin": origin, "User-Agent": "gradio-client"})
                        elif hasattr(self.client, '_client') and hasattr(self.client._client, 'headers'):
                            if isinstance(self.client._client.headers, dict):
                                self.client._client.headers["Origin"] = origin
                                self.client._client.headers["User-Agent"] = "gradio-client"
                        logger.info(f"✅ Connected to Bert-VITS2 server (retry successful)")
                    except Exception as retry_error:
                        logger.error(f"❌ Retry also failed: {retry_error}")
                        raise
                else:
                    raise
        return self.client

    def generate_audio(self, text: str, file_name_no_ext: str | None = None) -> str:
        """
        Generate speech audio file using Bert-VITS2 TTS.

        Args:
            text: The text to speak
            file_name_no_ext: Name of the file without file extension (optional)

        Returns:
            str: The path to the generated audio file
        """
        # Clean text (remove special markers)
        cleaned_text = re.sub(r"\[.*?\]", "", text)

        if len(cleaned_text) < 2:
            logger.warning("Text too short for TTS generation")
            return ""

        try:
            client = self._get_client()

            # 수정: gradio-client 2.x에 맞게 파라미터 이름 변경
            # reference_audio는 Audio 타입이므로 None 또는 파일 경로를 전달
            reference_audio = None
            if self.reference_audio_path:
                reference_audio = self.reference_audio_path
            
            # 수정: WebSocket 403 에러 해결을 위해 submit + result() 방식 사용 (HTTP만 사용)
            # app.py의 tts_fn 함수 시그니처에 맞게 파라미터 순서 조정
            # 순서: model_name, model_path, text, language, reference_audio_path, sdp_ratio,
            #       noise_scale, noise_scale_w, length_scale, line_split, split_interval,
            #       assist_text, assist_text_weight, use_assist_text, style, style_weight,
            #       kata_tone_json_str, use_tone, speaker
            # 참고: app.py에서는 assist_text, assist_text_weight, use_assist_text를 사용하지만
            #       Gradio UI에서는 style_text, style_text_weight, use_style_text로 표시됨
            #       실제 함수 파라미터는 assist_text를 사용하므로 위치 인자로 전달
            
            # 수정: use_ws=False로 설정했으므로 submit() + result() 방식 사용
            # HTTP 모드에서는 submit() + result()가 올바르게 작동해야 함
            # 수정: gradio_client의 deserialize 문제를 피하기 위해 직접 HTTP API 호출 사용
            # submit() + result()는 오디오 파일 deserialize에서 실패하므로 _predict_via_http 사용
            logger.info("🌐 Using direct HTTP API call (bypassing gradio_client deserialize)...")
            
            # HTTP API를 직접 호출하여 WebSocket 완전 우회 및 deserialize 문제 해결
            data = [
                self.model_name,  # model_name
                self.model_path,  # model_path
                cleaned_text,  # text
                self.language,  # language
                reference_audio,  # reference_audio_path
                self.sdp_ratio,  # sdp_ratio
                self.noise_scale,  # noise_scale
                self.noise_scale_w,  # noise_scale_w
                self.length_scale,  # length_scale
                self.line_split,  # line_split
                self.split_interval,  # split_interval
                self.style_text if self.use_style_text else "",  # assist_text
                self.style_text_weight,  # assist_text_weight
                self.use_style_text,  # use_assist_text
                self.style,  # style
                self.style_weight,  # style_weight
                "",  # kata_tone_json_str
                False,  # use_tone
                self.speaker,  # speaker
            ]
            
            # HTTP API 직접 호출
            # 수정: _predict_via_http가 (message, audio_tuple, kata_tone) 튜플을 반환함
            message, audio_tuple, kata_tone = self._predict_via_http(fn_index=16, data=data)
            
            # audio_tuple should be (sample_rate, audio_array)
            if audio_tuple is None:
                logger.error(f"❌ TTS generation failed: {message}")
                return ""

            if not isinstance(audio_tuple, (tuple, list)) or len(audio_tuple) < 2:
                logger.error(f"❌ TTS generation failed: Invalid audio format: {audio_tuple}")
                return ""

            sample_rate, audio_data = audio_tuple[0], audio_tuple[1]

            # Save audio to file
            file_name = self.generate_cache_file_name(file_name_no_ext, "wav")

            import scipy.io.wavfile as wavfile

            wavfile.write(file_name, sample_rate, audio_data)

            logger.info(f"✅ Generated audio: {file_name} | {message}")
            return file_name

        except Exception as e:
            import traceback
            error_msg = str(e) if e else "Unknown error"
            error_traceback = traceback.format_exc()
            logger.error(f"❌ Error generating audio with Bert-VITS2: {error_msg}")
            logger.error(f"Full traceback:\n{error_traceback}")  # 수정: DEBUG에서 ERROR로 변경하여 항상 출력
            
            # 수정: 에러 메시지가 None이 아닌지 확인 후 처리
            # WebSocket 403 에러인 경우 클라이언트 재생성 시도
            if error_msg and ("403" in error_msg or "WebSocket" in error_msg or "rejected" in error_msg):
                logger.warning("⚠️  WebSocket connection issue detected, resetting client...")
                self.client = None
                try:
                    client = self._get_client()
                    logger.info("✅ Client reset successful, retrying audio generation...")
                    # 재시도는 호출자가 처리하도록 빈 문자열 반환
                except Exception as retry_error:
                    logger.error(f"❌ Failed to reset client: {retry_error}")
            
            return ""
