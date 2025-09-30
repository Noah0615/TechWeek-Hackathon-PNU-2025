# 🚀 Career Navigator - AI 이력서 분석 및 커리어 로드맵 서비스

**Career Navigator**는 사용자의 이력서를 AI로 심층 분석하여, 목표 직무와의 적합도를 진단하고 개인 맞춤형 커리어 성장 로드맵을 제공하는 웹 애플리케이션입니다. 본 프로젝트는 **TechWeek Hackathon PNU 2025** 출품작입니다.

---

## ✨ 주요 기능 (Features)

이 프로젝트는 사용자의 커리어 여정을 돕기 위한 **4가지 핵심 기능**을 목표로 기획되었으며, 현재 **모든 기능이 구현**되어 있습니다.

### ✅ 1. AI 직무 적합도 분석
- 사용자가 **이력서 이미지 파일**과 **목표 직무**를 업로드하면, AI가 자동으로 이력서를 분석합니다.
- 단순 키워드 매칭을 넘어, **지원자의 강점, 보완점, 직무에 맞는 어필 전략**까지 상세하게 제공합니다.

### ✅ 2. 개인별 커리어 로드맵 제공
- 분석 결과를 바탕으로, **경력 경로와 예상 소요 시간**을 시각적으로 제시하여 커리어 성장을 위한 구체적인 로드맵을 제공합니다.

### ✅ 3. 추천 커리어 탐색
- 목표 직무가 없는 사용자를 위해, **이력서만으로 적합한 커리어 경로**를 추천하는 기능입니다.

### ✅ 4. 글로벌 커리어 맵
- 다양한 직업 생태계를 시각적인 지도로 보여주고, **직무 간 관계와 커리어 전환 경로**를 탐색할 수 있는 기능입니다.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Google Gemini (gemini-2.5-pro)
- **Libraries**: uvicorn, pandas, google-generativeai, python-multipart, jinja2, markdown-it-py, Pillow, folium

---

## 🏁 시작하기 (Getting Started)

### 1. 프로젝트 클론

```bash
git clone https://github.com/noah0615/techweek-hackathon-pnu-2025.git
cd techweek-hackathon-pnu-2025/TechWeek_Hackathon2
```

### 2. 필요 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 3. API 키 설정

프로젝트 루트 디렉토리(`TechWeek_Hackathon2`)에 `.env` 파일 생성 후, Google AI Studio에서 발급받은 API 키 입력:

```bash
export GEMINI_API_KEY="여기에_발급받은_API_키를_붙여넣으세요"
```

### 4. 서버 실행

```bash
python app.py
```

실행 후, 웹 브라우저에서 http://127.0.0.1:8000 접속

---

## 🕹️ 사용 방법 (How to Use)

1. 웹 페이지 접속
2. 드롭다운 메뉴에서 분석할 **목표 직무 선택**
3. `'파일 선택'` 버튼으로 **이력서 이미지 업로드**
4. `'Analyze'` 버튼 클릭 → AI가 이력서를 분석하고, **상세 분석 리포트**를 제공합니다.

---

## 🧑‍💻 팀원 (Team)

- **전재원** — Match %
- **소피** — Suggested Career
- **Nyi Niy Htun** — Global Career Map
- **Hanwae Nyein** — Career Roadmap

---

## 📜 License

This project is created for TechWeek Hackathon PNU 2025.  
License terms will be updated after the hackathon.

---

## 📞 Contact

프로젝트에 대한 문의사항이나 피드백은 이슈를 통해 남겨주세요!
