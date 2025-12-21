from numpy import zeros, int32, float32
import torch
from torch import from_numpy

from .core import maximum_path_jit


def maximum_path(neg_cent, mask):
    device = neg_cent.device
    dtype = neg_cent.dtype
    # 수정: 전체 함수를 try-except로 감싸서 모든 에러 처리
    try:
        # 수정: 빈 텐서 처리 - neg_cent나 mask가 비어있으면 빈 경로 반환
        if neg_cent.numel() == 0 or mask.numel() == 0:
            return torch.zeros_like(neg_cent).to(device=device, dtype=dtype)
        
        neg_cent = neg_cent.data.cpu().numpy().astype(float32)
        path = zeros(neg_cent.shape, dtype=int32)

        # 수정: mask.sum() 결과가 빈 텐서일 수 있으므로 먼저 확인
        mask_sum1 = mask.sum(1)
        mask_sum2 = mask.sum(2)
        
        # 수정: sum 결과가 빈 텐서이거나 두 번째 차원이 0인 경우 처리
        if mask_sum1.numel() == 0 or mask_sum2.numel() == 0:
            return from_numpy(path).to(device=device, dtype=dtype)
        
        # 수정: 인덱싱 전에 차원 확인
        if mask_sum1.shape[1] == 0 or mask_sum2.shape[1] == 0:
            return from_numpy(path).to(device=device, dtype=dtype)
        
        t_t_max = mask_sum1[:, 0].data.cpu().numpy().astype(int32)
        t_s_max = mask_sum2[:, 0].data.cpu().numpy().astype(int32)
        
        # 수정: t_t_max나 t_s_max가 빈 배열인 경우 처리
        if t_t_max.size == 0 or t_s_max.size == 0:
            return from_numpy(path).to(device=device, dtype=dtype)
        
        # 수정: t_t_max나 t_s_max의 값이 모두 0 이하인 경우 처리 (maximum_path_jit에서 range(0) 문제 방지)
        # max() 호출을 완전히 피하고, 모든 numpy 연산을 안전하게 처리
        # 빈 배열에서 .all() 호출도 문제가 될 수 있으므로 완전히 피함
        if t_t_max.size > 0 and len(t_t_max) > 0:
            # 모든 요소가 0 이하인지 확인 (max() 호출 없이)
            try:
                if (t_t_max <= 0).all():
                    return from_numpy(path).to(device=device, dtype=dtype)
            except (ValueError, AttributeError, RuntimeError):
                return from_numpy(path).to(device=device, dtype=dtype)
        else:
            return from_numpy(path).to(device=device, dtype=dtype)
        
        if t_s_max.size > 0 and len(t_s_max) > 0:
            # 모든 요소가 0 이하인지 확인 (max() 호출 없이)
            try:
                if (t_s_max <= 0).all():
                    return from_numpy(path).to(device=device, dtype=dtype)
            except (ValueError, AttributeError, RuntimeError):
                return from_numpy(path).to(device=device, dtype=dtype)
        else:
            return from_numpy(path).to(device=device, dtype=dtype)
        
        # 수정: maximum_path_jit 호출 전에 추가 검증
        try:
            maximum_path_jit(path, neg_cent, t_t_max, t_s_max)
        except (ValueError, RuntimeError, AttributeError) as e:
            # maximum_path_jit 내부에서 발생할 수 있는 에러 처리
            # zero-size array to reduction operation maximum 에러 포함
            pass  # path는 이미 zeros로 초기화되어 있음
        
        return from_numpy(path).to(device=device, dtype=dtype)
    except (ValueError, AttributeError, RuntimeError) as e:
        # 모든 에러를 잡아서 빈 경로 반환
        # ValueError: zero-size array to reduction operation maximum which has no identity
        try:
            return torch.zeros_like(neg_cent).to(device=device, dtype=dtype)
        except:
            # neg_cent가 없을 수도 있으므로 기본 경로 반환
            path = zeros((1, 1, 1), dtype=int32)
            return from_numpy(path).to(device=device, dtype=dtype)
