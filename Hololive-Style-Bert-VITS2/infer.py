import torch

import commons
import utils
from models import SynthesizerTrn
from models_jp_extra import SynthesizerTrn as SynthesizerTrnJPExtra
from text import cleaned_text_to_sequence, get_bert
from text.cleaner import clean_text
from text.symbols import symbols
from common.log import logger


class InvalidToneError(ValueError):
    pass


def get_net_g(model_path: str, version: str, device: str, hps):
    if version.endswith("JP-Extra"):
        #logger.info("Using JP-Extra model")
        net_g = SynthesizerTrnJPExtra(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            **hps.model,
        ).to(device)
    else:
        #logger.info("Using normal model")
        net_g = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            **hps.model,
        ).to(device)
    net_g.state_dict()
    _ = net_g.eval()
    if model_path.endswith(".pth") or model_path.endswith(".pt"):
        _ = utils.load_checkpoint(model_path, net_g, None, skip_optimizer=True)
    elif model_path.endswith(".safetensors"):
        _ = utils.load_safetensors(model_path, net_g, True)
    else:
        raise ValueError(f"Unknown model format: {model_path}")
    return net_g


def get_text(
    text,
    language_str,
    hps,
    device,
    assist_text=None,
    assist_text_weight=0.7,
    given_tone=None,
):
    use_jp_extra = hps.version.endswith("JP-Extra")
    norm_text, phone, tone, word2ph = clean_text(text, language_str, use_jp_extra)
    
    # 수정: 빈 phoneme 배열 검증 - 텍스트 정규화 후 phoneme이 없는 경우 에러 발생
    if len(phone) == 0:
        raise ValueError(f"Text normalization resulted in empty phoneme array. Original text: '{text}', Normalized text: '{norm_text}'")
    
    if given_tone is not None:
        if len(given_tone) != len(phone):
            raise InvalidToneError(
                f"Length of given_tone ({len(given_tone)}) != length of phone ({len(phone)})"
            )
        tone = given_tone
    phone, tone, language = cleaned_text_to_sequence(phone, tone, language_str)

    if hps.data.add_blank:
        phone = commons.intersperse(phone, 0)
        tone = commons.intersperse(tone, 0)
        language = commons.intersperse(language, 0)
        for i in range(len(word2ph)):
            word2ph[i] = word2ph[i] * 2
        word2ph[0] += 1
    
    # 수정: word2ph가 비어있는 경우 처리
    if len(word2ph) == 0:
        raise ValueError(f"word2ph is empty after processing. Original text: '{text}', Normalized text: '{norm_text}'")
    
    bert_ori = get_bert(
        norm_text, word2ph, language_str, device, assist_text, assist_text_weight
    )
    del word2ph

    # BERT 길이 검증 및 폴백 처리
    phone_len = len(phone)
    bert_len = bert_ori.shape[-1] if bert_ori is not None else 0

    if bert_len == 0 or bert_len != phone_len:
        logger.warning(
            f"⚠️ BERT length mismatch: bert_len={bert_len}, phone_len={phone_len}. "
            f"Using zero tensors as fallback."
        )
        # 모든 BERT를 zero tensor로 폴백
        bert = torch.zeros(1024, phone_len)
        ja_bert = torch.zeros(1024, phone_len)
        en_bert = torch.zeros(1024, phone_len)
    elif language_str == "JP":
        bert = torch.zeros(1024, phone_len)
        ja_bert = bert_ori
        en_bert = torch.zeros(1024, phone_len)
    elif language_str == "EN":
        bert = torch.zeros(1024, phone_len)
        ja_bert = torch.zeros(1024, phone_len)
        en_bert = bert_ori
    else:
        # ZH는 더 이상 지원하지 않으므로 zero tensor 사용
        logger.warning(f"⚠️ Unsupported language: {language_str}. Using zero tensors.")
        bert = torch.zeros(1024, phone_len)
        ja_bert = torch.zeros(1024, phone_len)
        en_bert = torch.zeros(1024, phone_len)

    phone = torch.LongTensor(phone)
    tone = torch.LongTensor(tone)
    language = torch.LongTensor(language)
    return bert, ja_bert, en_bert, phone, tone, language


def infer(
    text,
    style_vec,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    sid: int,  # In the original Bert-VITS2, its speaker_name: str, but here it's id
    language,
    hps,
    net_g,
    device,
    skip_start=False,
    skip_end=False,
    assist_text=None,
    assist_text_weight=0.7,
    given_tone=None,
):
    is_jp_extra = hps.version.endswith("JP-Extra")
    bert, ja_bert, en_bert, phones, tones, lang_ids = get_text(
        text,
        language,
        hps,
        device,
        assist_text=assist_text,
        assist_text_weight=assist_text_weight,
        given_tone=given_tone,
    )
    if skip_start:
        phones = phones[3:]
        tones = tones[3:]
        lang_ids = lang_ids[3:]
        bert = bert[:, 3:]
        ja_bert = ja_bert[:, 3:]
        en_bert = en_bert[:, 3:]
    if skip_end:
        phones = phones[:-2]
        tones = tones[:-2]
        lang_ids = lang_ids[:-2]
        bert = bert[:, :-2]
        ja_bert = ja_bert[:, :-2]
        en_bert = en_bert[:, :-2]
    target_len = phones.size(0)
    if bert.shape[-1] != target_len:
        logger.warning(
            "BERT length mismatch after slicing (bert=%s, target=%s). Using zeros.",
            bert.shape[-1],
            target_len,
        )
        bert = torch.zeros(bert.shape[0], target_len)
    if ja_bert.shape[-1] != target_len:
        logger.warning(
            "BERT length mismatch after slicing (ja_bert=%s, target=%s). Using zeros.",
            ja_bert.shape[-1],
            target_len,
        )
        ja_bert = torch.zeros(ja_bert.shape[0], target_len)
    if en_bert.shape[-1] != target_len:
        logger.warning(
            "BERT length mismatch after slicing (en_bert=%s, target=%s). Using zeros.",
            en_bert.shape[-1],
            target_len,
        )
        en_bert = torch.zeros(en_bert.shape[0], target_len)
    with torch.no_grad():
        x_tst = phones.to(device).unsqueeze(0)
        tones = tones.to(device).unsqueeze(0)
        lang_ids = lang_ids.to(device).unsqueeze(0)
        bert = bert.to(device).unsqueeze(0)
        ja_bert = ja_bert.to(device).unsqueeze(0)
        en_bert = en_bert.to(device).unsqueeze(0)
        x_tst_lengths = torch.LongTensor([phones.size(0)]).to(device)
        style_vec = torch.from_numpy(style_vec).to(device).unsqueeze(0)
        del phones
        sid_tensor = torch.LongTensor([sid]).to(device)
        target_len = x_tst.size(1)
        if tones.size(-1) != target_len:
            logger.warning(
                "Tone length mismatch (tones=%s, target=%s). Using zeros.",
                tones.size(-1),
                target_len,
            )
            tones = torch.zeros((1, target_len), dtype=tones.dtype, device=tones.device)
        if lang_ids.size(-1) != target_len:
            logger.warning(
                "Lang ID length mismatch (lang_ids=%s, target=%s). Using zeros.",
                lang_ids.size(-1),
                target_len,
            )
            lang_ids = torch.zeros(
                (1, target_len), dtype=lang_ids.dtype, device=lang_ids.device
            )
        if bert.size(-1) != target_len:
            logger.warning(
                "BERT length mismatch (bert=%s, target=%s). Using zeros.",
                bert.size(-1),
                target_len,
            )
            bert = torch.zeros(
                (1, bert.size(1), target_len), dtype=bert.dtype, device=bert.device
            )
        if ja_bert.size(-1) != target_len:
            logger.warning(
                "BERT length mismatch (ja_bert=%s, target=%s). Using zeros.",
                ja_bert.size(-1),
                target_len,
            )
            ja_bert = torch.zeros(
                (1, ja_bert.size(1), target_len),
                dtype=ja_bert.dtype,
                device=ja_bert.device,
            )
        if en_bert.size(-1) != target_len:
            logger.warning(
                "BERT length mismatch (en_bert=%s, target=%s). Using zeros.",
                en_bert.size(-1),
                target_len,
            )
            en_bert = torch.zeros(
                (1, en_bert.size(1), target_len),
                dtype=en_bert.dtype,
                device=en_bert.device,
            )
        def _infer_once():
            if is_jp_extra:
                return net_g.infer(
                    x_tst,
                    x_tst_lengths,
                    sid_tensor,
                    tones,
                    lang_ids,
                    ja_bert,
                    style_vec=style_vec,
                    sdp_ratio=sdp_ratio,
                    noise_scale=noise_scale,
                    noise_scale_w=noise_scale_w,
                    length_scale=length_scale,
                )
            return net_g.infer(
                x_tst,
                x_tst_lengths,
                sid_tensor,
                tones,
                lang_ids,
                bert,
                ja_bert,
                en_bert,
                style_vec=style_vec,
                sdp_ratio=sdp_ratio,
                noise_scale=noise_scale,
                noise_scale_w=noise_scale_w,
                length_scale=length_scale,
            )

        try:
            output = _infer_once()
        except RuntimeError as e:
            if "size of tensor" in str(e):
                logger.warning("Retrying inference with zeroed language/bert tensors.")
                tones = torch.zeros((1, target_len), dtype=tones.dtype, device=tones.device)
                lang_ids = torch.zeros((1, target_len), dtype=lang_ids.dtype, device=lang_ids.device)
                bert = torch.zeros((1, bert.size(1), target_len), dtype=bert.dtype, device=bert.device)
                ja_bert = torch.zeros((1, ja_bert.size(1), target_len), dtype=ja_bert.dtype, device=ja_bert.device)
                en_bert = torch.zeros((1, en_bert.size(1), target_len), dtype=en_bert.dtype, device=en_bert.device)
                output = _infer_once()
            else:
                raise
        audio = output[0][0, 0].data.cpu().float().numpy()
        del (
            x_tst,
            tones,
            lang_ids,
            bert,
            x_tst_lengths,
            sid_tensor,
            ja_bert,
            en_bert,
            style_vec,
        )  # , emo
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return audio


def infer_multilang(
    text,
    style_vec,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    sid,
    language,
    hps,
    net_g,
    device,
    skip_start=False,
    skip_end=False,
):
    bert, ja_bert, en_bert, phones, tones, lang_ids = [], [], [], [], [], []
    # emo = get_emo_(reference_audio, emotion, sid)
    # if isinstance(reference_audio, np.ndarray):
    #     emo = get_clap_audio_feature(reference_audio, device)
    # else:
    #     emo = get_clap_text_feature(emotion, device)
    # emo = torch.squeeze(emo, dim=1)
    for idx, (txt, lang) in enumerate(zip(text, language)):
        _skip_start = (idx != 0) or (skip_start and idx == 0)
        _skip_end = (idx != len(language) - 1) or skip_end
        (
            temp_bert,
            temp_ja_bert,
            temp_en_bert,
            temp_phones,
            temp_tones,
            temp_lang_ids,
        ) = get_text(txt, lang, hps, device)
        if _skip_start:
            temp_bert = temp_bert[:, 3:]
            temp_ja_bert = temp_ja_bert[:, 3:]
            temp_en_bert = temp_en_bert[:, 3:]
            temp_phones = temp_phones[3:]
            temp_tones = temp_tones[3:]
            temp_lang_ids = temp_lang_ids[3:]
        if _skip_end:
            temp_bert = temp_bert[:, :-2]
            temp_ja_bert = temp_ja_bert[:, :-2]
            temp_en_bert = temp_en_bert[:, :-2]
            temp_phones = temp_phones[:-2]
            temp_tones = temp_tones[:-2]
            temp_lang_ids = temp_lang_ids[:-2]
        bert.append(temp_bert)
        ja_bert.append(temp_ja_bert)
        en_bert.append(temp_en_bert)
        phones.append(temp_phones)
        tones.append(temp_tones)
        lang_ids.append(temp_lang_ids)
    bert = torch.concatenate(bert, dim=1)
    ja_bert = torch.concatenate(ja_bert, dim=1)
    en_bert = torch.concatenate(en_bert, dim=1)
    phones = torch.concatenate(phones, dim=0)
    tones = torch.concatenate(tones, dim=0)
    lang_ids = torch.concatenate(lang_ids, dim=0)
    with torch.no_grad():
        x_tst = phones.to(device).unsqueeze(0)
        tones = tones.to(device).unsqueeze(0)
        lang_ids = lang_ids.to(device).unsqueeze(0)
        bert = bert.to(device).unsqueeze(0)
        ja_bert = ja_bert.to(device).unsqueeze(0)
        en_bert = en_bert.to(device).unsqueeze(0)
        # emo = emo.to(device).unsqueeze(0)
        x_tst_lengths = torch.LongTensor([phones.size(0)]).to(device)
        del phones
        speakers = torch.LongTensor([hps.data.spk2id[sid]]).to(device)
        audio = (
            net_g.infer(
                x_tst,
                x_tst_lengths,
                speakers,
                tones,
                lang_ids,
                bert,
                ja_bert,
                en_bert,
                style_vec=style_vec,
                sdp_ratio=sdp_ratio,
                noise_scale=noise_scale,
                noise_scale_w=noise_scale_w,
                length_scale=length_scale,
            )[0][0, 0]
            .data.cpu()
            .float()
            .numpy()
        )
        del (
            x_tst,
            tones,
            lang_ids,
            bert,
            x_tst_lengths,
            speakers,
            ja_bert,
            en_bert,
        )  # , emo
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return audio
