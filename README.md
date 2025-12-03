# 📈 PatternCatcher - ML Server

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)

> **AI 주가 예측 및 차트 패턴 기반 실시간 감지·백테스팅 시스템**  
> 🏆 한이음 드림업 장려상 수상작

[![Organization](https://img.shields.io/badge/🏠_Organization-9D84B7?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SynergyX-AI-Pattern)
[![Main Server](https://img.shields.io/badge/📘_Main_Server-3396D3?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SynergyX-AI-Pattern/SynergyX-Server)
[![Client](https://img.shields.io/badge/📱_Client-B87C4C?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SynergyX-AI-Pattern/SynergyX-Client)

---

## 📌 Overview

**PatternCatcher**는 개인 투자자가 자신만의 차트 패턴을 정의하고,  
실시간 감지 및 백테스팅을 통해 투자 전략의 유효성을 검증할 수 있는 AI 투자 보조 시스템입니다.

**ML Server**는 DTW 기반 패턴 매칭, 백테스팅 연산, GRU 주가 예측, AI 종목 검색 및 감정 분석을 담당하는 **FastAPI 기반 AI/ML 서버**입니다. [Main Server](https://github.com/SynergyX-AI-Pattern/SynergyX-Server)로부터 요청을 받아 AI 분석을 수행하고 결과를 반환합니다.

### 주요 역할
- 📍 **실시간 패턴 감지** - DTW 알고리즘 기반 시계열 패턴 매칭 (평균 유사도 **0.85**)
- 📊 **백테스팅 엔진** - 과거 5년 데이터 기반 수익률 분석
- 🤖 **주가 예측** - GRU 모델 기반 15일 종가 예측 (MAPE **2.96%**)
- 🔍 **AI 종목 검색** - Vision AI + GPT-4o 이미지 분석
- 💭 **감정 일기 분석** - GPT-4o 기반 감정 분석 및 투자 조언

---

## 🛠 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Framework** | ![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?logo=gunicorn&logoColor=white) |
| **ML/AI** | ![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white) ![Keras](https://img.shields.io/badge/Keras-D00000?logo=keras&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white) |
| **Data Processing** | ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white) |
| **Database** | ![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white) |
| **Infrastructure** | ![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?logo=amazonec2&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) |
| **External API** | ![OpenAI](https://img.shields.io/badge/OpenAI_GPT--4o-412991?logo=openai&logoColor=white) ![Google Vision AI](https://img.shields.io/badge/Google_Vision_AI-4285F4?logo=google&logoColor=white) |

---

## 🏗 System Architecture

<img width="579" alt="System Architecture" src="https://github.com/user-attachments/assets/f7ae2bbf-5c16-4480-94c4-e54c5ca0359a" />

---

## 📁 Project Structure
```
app/
├── main.py                        # FastAPI main
├── api/v1/                        # API 라우터
│   └── endpoints/
│       ├── backtest.py
│       ├── pattern_detection.py
│       └── emotion_diary.py
├── services/                      # 비즈니스 로직
│   ├── backtest_service.py
│   ├── pattern_detection_service.py
│   ├── prediction_service.py
│   ├── image_search_service.py
│   └── external/
│       ├── gpt_service.py
│       └── vision_service.py
├── models/                        # DB 모델
├── schemas/                       # Pydantic 스키마
├── core/                          # 설정, 의존성
└── utils/                         # 유틸리티 (DTW, 정규화)
```

---

## 🚀 주요 기능

### 1. DTW 기반 실시간 패턴 감지
- Z-score 정규화 + FastDTW 알고리즘으로 효율적인 유사도 계산
- 평균 유사도 **0.85** 달성

### 2. 백테스팅 엔진
- 과거 5년 데이터 기반 전략 검증 및 수익률 분석
- 슬라이딩 윈도우 + 이진 탐색으로 고속 처리 (평균 **3초**)

### 3. GRU 기반 주가 예측
- 향후 15일 종가 예측 (MAPE **2.96%**, ±5% 이내 **82.9%**)
- 2층 GRU 모델로 높은 정확도 달성

### 4. AI 종목 검색
- Vision AI로 제품·로고·매장 사진에서 종목 추출
- GPT-4o 기반 상장 여부 자동 판별 및 종목 매칭

### 5. AI 감정 투자 일기
- GPT-4o 기반 감정 분석 및 투자 조언 제공
- 감정 분류, 키워드 추출, 일기 요약

---

## 📊 성능 지표

### 패턴 감지
- DTW 평균 유사도: **0.85**
- 알림 성공률: **99.0%**

### 주가 예측
- MAPE: **2.96%**
- NRMSE: **8.83%**
- ±5% 이내 예측률: **82.9%**

---

## 👥 Contributors

| | 한지수 | 조수민 |
|:---:|:------:|:------:|
| **GitHub** | [@eldeoddt](https://github.com/eldeoddt) | [@Soomxn](https://github.com/Soomxn) |
| **Role** | Team / Backend Lead | Backend / ML Engineer |
| **Profile** | <img width="120" src="https://avatars.githubusercontent.com/eldeoddt" /> | <img width="120" src="https://avatars.githubusercontent.com/Soomxn" /> |
| **담당** | <div align="left">• GRU 주가 예측 모델<br/>• FastAPI 서버 구축<br/>• GPT-4o & Vision AI 연동<br/>• 모델 학습 및 배포</div> | <div align="left">• DTW 패턴 감지 로직<br/>• 백테스팅 엔진 구현<br/>• AI 종목 검색<br/>• 감정 투자 일기 분석</div> |

---

## 🔗 Related Repositories

- [📘 Main Server](https://github.com/SynergyX-AI-Pattern/SynergyX-Server) - Spring Boot 기반 백엔드 서버
- [📱 Client](https://github.com/SynergyX-AI-Pattern/SynergyX-Client) - Flutter 모바일 앱

---

## 📧 Contact

**Email**: patterncatcher83@gmail.com

---

<div align="center">

**PatternCatcher ML Server** by Team SynergyX

© 2025 Team SynergyX. All rights reserved.

</div>
