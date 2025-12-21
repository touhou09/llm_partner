from huggingface_hub import hf_hub_download
import os
import shutil

# 저장할 디렉토리
save_dir = "model_assets/SBV2_HoloHi"
os.makedirs(save_dir, exist_ok=True)

print("Downloading SBV2_HoloHi model files...")

try:
    # 1. Config 파일 다운로드
    print("Downloading config.json...")
    config_path = hf_hub_download(
        repo_id="Kit-Lemonfoot/Hololive-Style-Bert-VITS2",
        subfolder="model_assets/SBV2_HoloHi",
        filename="config.json",
        local_dir="."
    )
    # 다운로드된 파일을 올바른 위치로 이동 (hf_hub_download는 구조를 유지하므로 필요 없을 수 있지만 안전하게)
    # local_dir="."로 하면 model_assets/SBV2_HoloHi/config.json 경로에 생김

    # 2. 모델 파일 다운로드
    print("Downloading safetensors...")
    model_path = hf_hub_download(
        repo_id="Kit-Lemonfoot/Hololive-Style-Bert-VITS2",
        subfolder="model_assets/SBV2_HoloHi",
        filename="SBV2_HoloHi.safetensors",
        local_dir="."
    )

    # 3. 스타일 벡터 다운로드
    print("Downloading style_vectors.npy...")
    style_path = hf_hub_download(
        repo_id="Kit-Lemonfoot/Hololive-Style-Bert-VITS2",
        subfolder="model_assets/SBV2_HoloHi",
        filename="style_vectors.npy",
        local_dir="."
    )

    print("\n✅ Download Complete!")
    print(f"Files saved in {save_dir}")

except Exception as e:
    print(f"\n❌ Download Failed: {e}")
