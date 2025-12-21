import sys

import torch
from transformers import DebertaV2Model, DebertaV2Tokenizer

from config import config


LOCAL_PATH = "./bert/deberta-v3-large"

tokenizer = DebertaV2Tokenizer.from_pretrained(LOCAL_PATH)

models = dict()


def get_bert_feature(
    text,
    word2ph,
    device=config.bert_gen_config.device,
    assist_text=None,
    assist_text_weight=0.7,
):
    if (
        sys.platform == "darwin"
        and torch.backends.mps.is_available()
        and device == "cpu"
    ):
        device = "mps"
    if not device:
        device = "cuda"
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"
    if device not in models.keys():
        # 수정: PyTorch/transformers 버전 호환성 문제 해결
        # meta tensor를 디바이스로 이동할 때 발생하는 에러 방지
        import warnings
        import os
        warnings.filterwarnings("ignore", category=UserWarning)
        
        # 수정: accelerate 라이브러리의 영향을 받지 않도록 환경 변수 설정
        # ACCELERATE_USE_CPU=1을 설정하여 CPU에 강제 로드
        original_accelerate = os.environ.get("ACCELERATE_USE_CPU", None)
        os.environ["ACCELERATE_USE_CPU"] = "1"
        os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
        
        try:
            # 수정: device_map=None과 low_cpu_mem_usage=False를 사용하여
            # 모델이 실제 데이터와 함께 CPU에 로드되도록 함
            # torch_dtype 대신 dtype 사용 (deprecation 경고 해결)
            try:
                model = DebertaV2Model.from_pretrained(
                    LOCAL_PATH,
                    device_map=None,  # meta device 사용 방지 (명시적)
                    low_cpu_mem_usage=False,  # meta device 사용 방지
                    dtype=torch.float32,  # torch_dtype 대신 dtype 사용
                )
            except TypeError:
                # 일부 transformers 버전에서는 device_map 파라미터를 지원하지 않을 수 있음
                model = DebertaV2Model.from_pretrained(
                    LOCAL_PATH,
                    low_cpu_mem_usage=False,
                    dtype=torch.float32,  # torch_dtype 대신 dtype 사용
                )
            
            # 수정: 모델이 meta device에 있는지 먼저 확인 (to() 호출 전)
            # 모든 파라미터를 확인하여 meta device에 있는지 체크
            has_meta_tensor = False
            try:
                for param in model.parameters():
                    if param.device.type == "meta":
                        has_meta_tensor = True
                        break
            except Exception:
                # 파라미터 확인 중 에러 발생 시 첫 번째 파라미터만 확인
                first_param = next(iter(model.parameters()))
                has_meta_tensor = (first_param.device.type == "meta")
            
            if has_meta_tensor:
                # meta device에 있다면 state_dict를 직접 로드하여 CPU에 배치
                try:
                    # PyTorch 2.0+에서 지원하는 to_empty() 사용
                    if hasattr(model, 'to_empty'):
                        model = model.to_empty(device="cpu")
                        # 가중치를 다시 로드
                        state_dict = torch.load(
                            f"{LOCAL_PATH}/pytorch_model.bin",
                            map_location="cpu",
                            weights_only=False
                        )
                        model.load_state_dict(state_dict, strict=False)
                    else:
                        # to_empty()가 지원되지 않는 경우, 모델을 다시 초기화
                        # config를 로드하여 모델 구조 재생성
                        from transformers import AutoConfig
                        config = AutoConfig.from_pretrained(LOCAL_PATH)
                        model = DebertaV2Model(config)
                        # state_dict 로드
                        state_dict = torch.load(
                            f"{LOCAL_PATH}/pytorch_model.bin",
                            map_location="cpu",
                            weights_only=False
                        )
                        model.load_state_dict(state_dict, strict=False)
                        model = model.to("cpu")
                except (AttributeError, FileNotFoundError, Exception) as e:
                    # 모든 방법이 실패한 경우, 최후의 수단으로 다시 로드
                    # 하지만 이번에는 더 강력한 옵션 사용
                    import logging
                    logging.warning(f"Failed to fix meta device issue: {e}, retrying with different options")
                    model = DebertaV2Model.from_pretrained(
                        LOCAL_PATH,
                        low_cpu_mem_usage=False,
                        torch_dtype=None,  # dtype 지정 안 함
                    )
                    # 다시 확인
                    first_param = next(iter(model.parameters()))
                    if first_param.device.type == "meta":
                        raise RuntimeError("Failed to load model to CPU (still on meta device after all attempts)")
                    # meta device에 없다면 CPU로 이동
                    model = model.to("cpu")
            else:
                # meta device에 없다고 확인되었지만, to() 호출 시 에러가 발생할 수 있음
                # 안전하게 try-except로 처리
                try:
                    model = model.to("cpu")
                    # 이동 후 다시 확인 (일부 파라미터가 여전히 meta device에 있을 수 있음)
                    for param in model.parameters():
                        if param.device.type == "meta":
                            raise NotImplementedError("Found meta tensor after to('cpu')")
                except NotImplementedError as e:
                    # to() 호출 시 또는 이동 후 meta tensor 발견 시
                    # state_dict를 직접 로드하여 해결
                    try:
                        state_dict = torch.load(
                            f"{LOCAL_PATH}/pytorch_model.bin",
                            map_location="cpu",
                            weights_only=False
                        )
                        # 모델 구조 재생성
                        from transformers import AutoConfig
                        config = AutoConfig.from_pretrained(LOCAL_PATH)
                        model = DebertaV2Model(config)
                        model.load_state_dict(state_dict, strict=False)
                        # 이제는 확실히 CPU에 있음
                    except Exception as e2:
                        raise RuntimeError(f"Failed to load model to CPU using state_dict: {e2}") from e
            
        finally:
            # 환경 변수 복원
            if original_accelerate is not None:
                os.environ["ACCELERATE_USE_CPU"] = original_accelerate
            elif "ACCELERATE_USE_CPU" in os.environ:
                del os.environ["ACCELERATE_USE_CPU"]
        
        # 수정: 모델이 이미 CPU에 로드되었으므로, 디바이스가 CPU가 아닌 경우에만 이동
        # 수정: 모델이 이미 해당 디바이스에 있는지 확인하여 불필요한 이동 방지 (메모리 절약)
        if device != "cpu":
            # 모델의 첫 번째 파라미터를 확인하여 현재 디바이스 확인
            try:
                first_param = next(iter(model.parameters()))
                current_device = str(first_param.device)
                target_device = f"cuda:{torch.cuda.current_device()}" if device == "cuda" else device
                
                # 모델이 이미 해당 디바이스에 있으면 이동하지 않음
                if current_device == target_device or (device == "cuda" and "cuda" in current_device):
                    pass  # 이미 올바른 디바이스에 있음
                else:
                    # CUDA 메모리 정리 시도
                    if device == "cuda" and torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    model = model.to(device)
            except Exception as e:
                # 파라미터 확인 실패 시 안전하게 이동 시도
                import logging
                logging.warning(f"Failed to check model device, attempting to move: {e}")
                if device == "cuda" and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                model = model.to(device)
        models[device] = model
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors="pt")
        for i in inputs:
            inputs[i] = inputs[i].to(device)
        res = models[device](**inputs, output_hidden_states=True)
        res = torch.cat(res["hidden_states"][-3:-2], -1)[0].cpu()
        if assist_text:
            style_inputs = tokenizer(assist_text, return_tensors="pt")
            for i in style_inputs:
                style_inputs[i] = style_inputs[i].to(device)
            style_res = models[device](**style_inputs, output_hidden_states=True)
            style_res = torch.cat(style_res["hidden_states"][-3:-2], -1)[0].cpu()
            style_res_mean = style_res.mean(0)
    assert len(word2ph) == res.shape[0], (text, res.shape[0], len(word2ph))
    word2phone = word2ph
    phone_level_feature = []
    for i in range(len(word2phone)):
        if assist_text:
            repeat_feature = (
                res[i].repeat(word2phone[i], 1) * (1 - assist_text_weight)
                + style_res_mean.repeat(word2phone[i], 1) * assist_text_weight
            )
        else:
            repeat_feature = res[i].repeat(word2phone[i], 1)
        phone_level_feature.append(repeat_feature)

    phone_level_feature = torch.cat(phone_level_feature, dim=0)

    return phone_level_feature.T
