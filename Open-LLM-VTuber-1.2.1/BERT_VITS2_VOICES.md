# BERT-VITS2 사용 가능한 보이스 목록

이 파일은 Hololive-Style-Bert-VITS2 TTS 서버에서 사용 가능한 모든 보이스 모델을 정리한 것입니다.

## 설정 방법

`conf.yaml`의 `bert_vits2_tts` 섹션에서 다음 필드를 수정하세요:
- `model_name`: 보이스의 짧은 이름 (예: 'Kiara', 'Gura')
- `model_path`: 모델 경로 (예: 'SBV2_TakanashiKiara')
- `speaker`: 화자 ID (예: 'TakanashiKiara')
- `language`: 'EN' (영어) 또는 'JP' (일본어)

## 영어(EN) 보이스

### HoloMyth (1기)
| 이름 | model_name | model_path | speaker | 설명 |
|------|------------|------------|---------|------|
| Mori Calliope | Calli | SBV2_HoloLow | MoriCalliope | 저음 보이스 |
| Takanashi Kiara | Kiara | SBV2_TakanashiKiara | TakanashiKiara | 전용 모델 |
| Ninomae Ina'nis | Ina | SBV2_HoloHi | NinomaeInanis | 고음 보이스 |
| Gawr Gura | Gura | SBV2_HoloHi | GawrGura | 고음 보이스 |
| Amelia Watson | Amelia | SBV2_HoloHi | AmeliaWatson | 고음 보이스 |

### Project: HOPE
| 이름 | model_name | model_path | speaker | 설명 |
|------|------------|------------|---------|------|
| IRyS | IRyS | SBV2_HoloHi | IRyS | 고음 보이스 |

### HoloCouncil (2기)
| 이름 | model_name | model_path | speaker | 설명 |
|------|------------|------------|---------|------|
| Tsukumo Sana | Sana | SBV2_HoloAus | TsukumoSana | 호주식 억양 |
| Ceres Fauna | Fauna | SBV2_HoloHi | CeresFauna | 고음 보이스 |
| Ouro Kronii | Kronii | SBV2_HoloLow | OuroKronii | 저음 보이스 |
| Nanashi Mumei | Mumei | SBV2_HoloHi | NanashiMumei | 고음 보이스 |
| Hakos Baelz | Baelz | SBV2_HoloAus | HakosBaelz | 호주식 억양 |

### HoloAdvent (3기)
| 이름 | model_name | model_path | speaker | 설명 |
|------|------------|------------|---------|------|
| Shiori Novella | Shiori | SBV2_HoloHi | ShioriNovella | 고음 보이스 |
| Koseki Bijou | Bijou | SBV2_KosekiBijou | KosekiBijou | 전용 모델 |
| Nerissa Ravencroft | Nerissa | SBV2_HoloLow | NerissaRavencroft | 저음 보이스 |

### HoloID (인도네시아)
| 이름 | model_name | model_path | speaker | 설명 |
|------|------------|------------|---------|------|
| Ayunda Risu | Risu | SBV2_HoloESL | AyundaRisu | ESL 억양 |
| Moona Hoshinova | Moona | SBV2_HoloESL | MoonaHoshinova | ESL 억양 |
| Airani Iofifteen | Iofi | SBV2_HoloESL | AiraniIofifteen | ESL 억양 |
| Kureiji Ollie | Ollie | SBV2_HoloIDFlu | KureijiOllie | 유창한 영어 |
| Anya Melfissa | Anya | SBV2_HoloESL | AnyaMelfissa | ESL 억양 |
| Vestia Zeta | Zeta | SBV2_HoloIDFlu | VestiaZeta | 유창한 영어 |
| Kobo Kanaeru | Kobo | SBV2_HoloESL | KoboKanaeru | ESL 억양 |

## 일본어(JP) 보이스

### 0기생
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Tokino Sora | Sora | SBV2_HoloJPTest2 | TokinoSora |
| Sakura Miko | Miko | SBV2_HoloJPBaby | SakuraMiko |
| Hoshimachi Suisei | Suisei | SBV2_HoloJPTest2 | HoshimachiSuisei |
| AZKi | AZKi | SBV2_HoloJPTest2.5 | AZKi |

### 1기생
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Yozora Mel | Mel | SBV2_HoloJPTest2.5 | YozoraMel |
| Shirakami Fubuki | Fubuki | SBV2_HoloJPTest3 | ShirakamiFubuki |
| Natsuiro Matsuri | Matsuri | SBV2_HoloJPTest2.5 | NatsuiroMatsuri |
| Aki Rosenthal | Aki | SBV2_HoloJPTest2.5 | AkiRosenthal |
| Akai Haato | Haato | SBV2_HoloJPTest2.5 | AkaiHaato |

### 2기생
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Minato Aqua | Aqua | SBV2_HoloJPTest2 | MinatoAqua |
| Nakiri Ayame | Ayame | SBV2_HoloJPTest2 | NakiriAyame |
| Oozora Subaru | Subaru | SBV2_HoloJPTest3 | OozoraSubaru |

### GAMERS
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Nekomata Okayu | Okayu | SBV2_HoloJPTest | NekomataOkayu |

### 3기생
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Usada Pekora | Pekora | SBV2_UsadaPekora | UsadaPekora |
| Pekomama | Pekomama | SBV2_UsadaPekora | Pekomama |
| Uruha Rushia | Rushia | SBV2_HoloJPTest3 | UruhaRushia |
| Shiranui Flare | Flare | SBV2_HoloJPTest | ShiranuiFlare |
| Shirogane Noel | Noel | SBV2_HoloJPTest | ShiroganeNoel |
| Houshou Marine | Marine | SBV2_HoloJPTest | HoushouMarine |

### 4기생
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Amane Kanata | Kanata | SBV2_HoloJPTest3 | AmaneKanata |
| Tsunomaki Watame | Watame | SBV2_HoloJPTest3 | TsunomakiWatame |
| Tokoyami Towa | Towa | SBV2_HoloJPTest2 | TokoyamiTowa |
| Himemori Luna | Luna | SBV2_HoloJPBaby | HimemoriLuna |

### 5기생
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Yukihana Lamy | Lamy | SBV2_HoloJPTest2 | YukihanaLamy |
| Momosuzu Nene | Nene | SBV2_HoloJPTest3 | MomosuzuNene |
| Omaru Polka | Polka | SBV2_HoloJPTest3 | OmaruPolka |

### holoX (6기생)
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| La+ Darknesss | Laplus | SBV2_HoloJPTest | LaplusDarknesss |
| Takane Lui | Lui | SBV2_HoloJPTest2.5 | TakaneLui |
| Hakui Koyori | Koyori | SBV2_HoloJPTest2 | HakuiKoyori |
| Sakamata Chloe | Chloe | SBV2_HoloJPTest2 | SakamataChloe |

### ReGLOSS
| 이름 | model_name | model_path | speaker |
|------|------------|------------|---------|
| Ichijou Ririka | Ririka | SBV2_HoloJPTest | IchijouRirika |
| Juufuutei Raden | Raden | SBV2_HoloJPTest3 | JuufuuteiRaden |

## 사용 예시

### 영어 보이스 (Gawr Gura)
```yaml
bert_vits2_tts:
  client_url: 'http://127.0.0.1:7860'
  model_name: 'Gura'
  model_path: 'SBV2_HoloHi'
  speaker: 'GawrGura'
  language: 'EN'
  style: 'Neutral'
  style_weight: 3.0
```

### 일본어 보이스 (Usada Pekora)
```yaml
bert_vits2_tts:
  client_url: 'http://127.0.0.1:7860'
  model_name: 'Pekora'
  model_path: 'SBV2_UsadaPekora'
  speaker: 'UsadaPekora'
  language: 'JP'
  style: 'Neutral'
  style_weight: 3.0
```

## 스타일 옵션

각 모델은 다양한 스타일 프리셋을 지원합니다 (모델의 config.json에 정의됨):
- **Neutral**: 기본 중립 스타일
- 기타 감정 스타일은 모델마다 다를 수 있음

`style_weight` (0-20)로 스타일 강도를 조절할 수 있습니다.

## 참고사항

- BERT-VITS2 Gradio 서버가 `http://127.0.0.1:7860`에서 실행 중이어야 합니다
- 모델은 `Hololive-Style-Bert-VITS2/model_assets/` 디렉토리에 있어야 합니다
- 일부 모델은 전용 모델 파일을 가지고 있으며, 다른 모델은 공유 모델을 사용합니다
