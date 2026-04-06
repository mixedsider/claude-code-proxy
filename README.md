# Gemini, GPT 및 로컬LLM 을 위한 Anthropic API 프록시 🔄

**Claude Code와 같은 Anthropic 클라이언트를 Gemini, OpenAI, LM Studio, Ollama 또는 직접적인 Anthropic 백엔드와 함께 사용하세요.** 🤝

Anthropic 클라이언트를 Gemini, OpenAI 또는 Anthropic 모델 자체(일종의 투명 프록시)와 함께 사용할 수 있게 해주는 프록시 서버입니다. 모든 과정은 LiteLLM을 통해 이루어집니다. 🌉


![Anthropic API 프록시](pic.png)

## 빠른 시작 ⚡

### 사전 요구 사항

- OpenAI API 키 🔑
- Google AI Studio (Gemini) API 키 (Google 제공자를 사용하는 경우) 🔑
- Vertex AI API가 활성화된 Google Cloud 프로젝트 (Gemini에 애플리케이션 기본 자격 증명을 사용하는 경우) ☁️
- [uv](https://github.com/astral-sh/uv) 설치됨.

### 설치 및 실행 방법 🚀

이 프록시는 [uv](https://github.com/astral-sh/uv)를 사용하여 의존성을 관리합니다. 운영체제에 맞는 스크립트를 사용하여 간단히 시작할 수 있습니다.

#### 1. 저장소 복제 및 이동
```bash
git clone https://github.com/mixedsider/claude-code-proxy.git
cd claude-code-proxy
```

#### 2. 서버 설정 및 가동

**리눅스 / macOS:**
```bash
chmod +x install.sh start.sh
./install.sh  # 최초 1회 실행: 환경 설정 (.env 생성 및 uv 설치 확인)
./start.sh    # 서버 실행
```

**윈도우 (PowerShell):**
```powershell
.\install.ps1  # 최초 1회 실행: 환경 설정 (.env 생성 및 uv 설치 확인)
.\start.ps1    # 서버 실행
```

> [!NOTE]
> `install` 스크립트는 `uv`가 없는 경우 자동으로 설치하고, `.env.example`을 기반으로 `.env` 파일을 생성해 줍니다. 생성된 **.env** 파일을 열어 API 키를 입력한 후 서버를 실행하세요.

#### 3. 수동 실행 (고급 사용자)
스크립트를 사용하지 않고 직접 실행하려면 아래 명령어를 사용하세요:
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

### 환경 변수 설정 (.env) 🛠️

`.env` 파일에서 다음 항목들을 설정하여 프록시의 동작을 제어할 수 있습니다:

*   `ANTHROPIC_API_KEY`: (선택 사항) Anthropic 모델로 직접 프록시하는 경우 필요.
*   `OPENAI_API_KEY`: OpenAI API 키.
*   `GEMINI_API_KEY`: Google AI Studio (Gemini) API 키.
*   **3단계 모델 계층 설정 (선택 사항)**:
    *   `BIG_MODEL_PROVIDER` / `BIG_MODEL`: `opus` 매핑용.
    *   `MIDDLE_MODEL_PROVIDER` / `MIDDLE_MODEL`: `sonnet` 매핑용 (기본값: LM Studio / gemma-4-31b-it).
    *   `SMALL_MODEL_PROVIDER` / `SMALL_MODEL`: `haiku` 매핑용 (기본값: Ollama / gemma4:e4b-it-q4_K_M).

### 테스트 수행 🧪

서버 가동 후, `tests.py`를 사용하여 다양한 시나리오를 테스트할 수 있습니다. 주요 테스트 케이스는 다음과 같습니다.

#### 1. 프록시 서버 기본 동작 테스트 (Anthropic 비교 제외)
외부 Anthropic API와의 비교 없이 프록시 서버의 응답 구조가 올바른지만 확인합니다. (API 키가 없어도 로컬 모델 테스트 시 유용합니다)
```bash
uv run python tests.py --proxy-only
```

#### 2. 특정 모델 및 계층 지정 테스트
특정 계층(Big, Middle, Small)이나 로컬 모델(`ollama`, `lm_studio`)만 콕 집어서 테스트하고 싶을 때 사용합니다.
```bash
# BIG(Opus) 계층 매핑 테스트
uv run python tests.py --test tier_big --proxy-only

# MIDDLE(Sonnet) 계층 매핑 테스트
uv run python tests.py --test tier_middle --proxy-only

# SMALL(Haiku) 계층 매핑 테스트
uv run python tests.py --test tier_small --proxy-only

# Ollama 직접 호출 테스트
uv run python tests.py --test ollama --proxy-only
```

#### 3. 전체 모델 계층 통합 테스트
설정된 BIG, MIDDLE, SMALL 전 계층의 매핑과 응답을 한 번에 확인합니다.
```bash
uv run python tests.py --tiers --proxy-only
```

#### Docker 사용

Docker를 사용하는 경우, 위에 설명된 대로 예시 환경 파일을 `.env`로 다운로드하고 편집합니다.
```bash
curl -O .env https://raw.githubusercontent.com/1rgs/claude-code-proxy/refs/heads/main/.env.example
```

그런 다음, [docker compose](https://docs.docker.com/compose/)를 사용하여 컨테이너를 시작할 수 있습니다 (권장):

```yml
services:
  proxy:
    image: ghcr.io/1rgs/claude-code-proxy:latest
    restart: unless-stopped
    env_file: .env
    ports:
      - 8082:8082
```

또는 명령어로 실행:

```bash
docker run -d --env-file .env -p 8082:8082 ghcr.io/1rgs/claude-code-proxy:latest
```

### Claude Code와 함께 사용하기 🎮

1. **Claude Code 설치** (아직 설치하지 않은 경우):
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **프록시에 연결**:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:8082 claude
   ```

3. **완료되었습니다!** 이제 Claude Code 클라이언트는 프록시를 통해 설정된 백엔드 모델(기본값 Gemini)을 사용합니다. 🎯

## 모델 매핑 🗺️

프록시는 Claude의 3단계 모델 계층을 사용자가 정의한 백엔드 모델로 자동 매핑합니다:

| 계층 | Claude 모델 키워드 | 매핑 대상 (기본값/예시) | 프로바이더 예시 |
| :--- | :--- | :--- | :--- |
| **BIG** | `opus` / `sonnet` (설정에 따라) | `BIG_MODEL` (예: `gemini-2.5-pro`) | Google Gemini / OpenAI |
| **MIDDLE** | `sonnet` | `MIDDLE_MODEL` (예: `gemma-4-31b-it`) | LM Studio / Local |
| **SMALL** | `haiku` | `SMALL_MODEL` (예: `gemma2:2b`) | Ollama / Local |

### 하이브리드(Hybrid) 구성 예시 🌟

가장 강력한 기능 중 하나는 외부 API와 로컬 모델을 혼합하여 사용하는 것입니다. `.env` 파일에서 다음과 같이 설정할 수 있습니다:

```dotenv
# BIG 모델은 Gemini Pro 사용 (외부 API)
BIG_MODEL_PROVIDER="google"
BIG_MODEL="gemini-2.5-pro"

# MIDDLE 모델은 LM Studio의 Gemma 사용 (로컬)
MIDDLE_MODEL_PROVIDER="lm-studio"
MIDDLE_MODEL="gemma-4-31b-it"

# SMALL 모델은 Ollama 사용 (로컬)
SMALL_MODEL_PROVIDER="ollama"
SMALL_MODEL="gemma4:e4b-it-q4_K_M"

# API 키 설정
GEMINI_API_KEY="AIza..."
OPENAI_API_KEY="sk-..."
```

이렇게 설정하면 Claude Code에서 `sonnet` 모델을 요청할 때 실제로는 로컬의 `gemma-4-31b-it` 모델이 동작하게 됩니다.

### 지원되는 모델

#### OpenAI 모델
다음 OpenAI 모델은 자동 `openai/` 접두사 처리가 지원됩니다:
- o3-mini
- o1
- o1-mini
- o1-pro
- gpt-4.5-preview
- gpt-4o
- gpt-4o-audio-preview
- chatgpt-4o-latest
- gpt-4o-mini
- gpt-4o-mini-audio-preview
- gpt-4.1
- gpt-4.1-mini

#### Gemini 모델
다음 Gemini 모델은 자동 `gemini/` 접두사 처리가 지원됩니다:
- gemini-2.5-pro
- gemini-2.5-flash

### 모델 접두사 처리
프록시는 모델 이름에 적절한 접두사를 자동으로 추가합니다:
- OpenAI 모델은 `openai/` 접두사가 붙습니다.
- Gemini 모델은 `gemini/` 접두사가 붙습니다.
- BIG_MODEL 및 SMALL_MODEL은 OpenAI 또는 Gemini 모델 목록에 있는지 여부에 따라 적절한 접두사가 붙습니다.

예시:
- `gpt-4o`는 `openai/gpt-4o`가 됩니다.
- `gemini-2.5-pro-preview-03-25`는 `gemini/gemini-2.5-pro-preview-03-25`가 됩니다.
- BIG_MODEL이 Gemini 모델로 설정된 경우, Claude Sonnet은 `gemini/[모델명]`으로 매핑됩니다.

### 모델 매핑 사용자 정의

`.env` 파일의 환경 변수를 사용하거나 직접 매핑을 제어할 수 있습니다:

**예시 1: 기본값 (OpenAI 사용)**
API 키 외에는 `.env`를 변경할 필요가 없거나 다음과 같이 설정합니다:
```dotenv
OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-google-key" # PREFERRED_PROVIDER=google인 경우 필요
# PREFERRED_PROVIDER="openai" # 선택 사항, 기본값임
# BIG_MODEL="gpt-4.1" # 선택 사항, 기본값임
# SMALL_MODEL="gpt-4.1-mini" # 선택 사항, 기본값임
```

**예시 2a: Google 선호 (GEMINI_API_KEY 사용)**
```dotenv
GEMINI_API_KEY="your-google-key"
OPENAI_API_KEY="your-openai-key" # 폴백을 위해 필요
PREFERRED_PROVIDER="google"
# BIG_MODEL="gemini-2.5-pro" # 선택 사항, Google 선호 시 기본값
# SMALL_MODEL="gemini-2.5-flash" # 선택 사항, Google 선호 시 기본값
```

**예시 2b: Google 선호 (애플리케이션 기본 자격 증명과 함께 Vertex AI 사용)**
```dotenv
OPENAI_API_KEY="your-openai-key" # 폴백을 위해 필요
PREFERRED_PROVIDER="google"
VERTEX_PROJECT="your-gcp-project-id"
VERTEX_LOCATION="us-central1"
USE_VERTEX_AUTH=true
# BIG_MODEL="gemini-2.5-pro" # 선택 사항, Google 선호 시 기본값
# SMALL_MODEL="gemini-2.5-flash" # 선택 사항, Google 선호 시 기본값
```

**예시 3: 직접 Anthropic 사용 ("단순 Anthropic 프록시" 모드)**
```dotenv
ANTHROPIC_API_KEY="sk-ant-..."
PREFERRED_PROVIDER="anthropic"
# 이 모드에서 BIG_MODEL 및 SMALL_MODEL은 무시됩니다.
# haiku/sonnet 요청은 Anthropic 모델로 직접 전달됩니다.
```

*사용 사례: 이 모드는 OpenAI나 Gemini로 재매핑하지 않고 실제 Anthropic 모델을 사용하면서도 프록시 인프라(로깅, 미들웨어, 요청/응답 처리 등)를 활용하고 싶을 때 유용합니다.*

**예시 4: 특정 OpenAI 모델 사용**
```dotenv
OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-google-key"
PREFERRED_PROVIDER="openai"
BIG_MODEL="gpt-4o" # 특정 모델 예시
SMALL_MODEL="gpt-4o-mini" # 특정 모델 예시
```

**예시 5: Ollama 사용**
```dotenv
PREFERRED_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434" # 기본값
BIG_MODEL="llama3.3"
SMALL_MODEL="llama3.1:8b"
```

**예시 6: LM Studio 사용**
```dotenv
PREFERRED_PROVIDER="lm-studio"
LM_STUDIO_BASE_URL="http://localhost:1234/v1" # 기본값
BIG_MODEL="qwen2.5-7b-instruct"
SMALL_MODEL="qwen2.5-1.5b-instruct"
```

## 작동 원리 🧩

이 프록시는 다음과 같이 작동합니다:

1. Anthropic의 API 형식으로 **요청을 받음** 📥
2. LiteLLM을 통해 요청을 OpenAI 형식으로 **번역** 🔄
3. 번역된 요청을 백엔드(OpenAI 등)로 **전송** 📤
4. 응답을 다시 Anthropic 형식으로 **변환** 🔄
5. 형식화된 응답을 클라이언트에 **반환** ✅

프록시는 스트리밍 및 비스트리밍 응답을 모두 처리하며, 모든 Claude 클라이언트와의 호환성을 유지합니다. 🌊

## 기여하기 🤝

기여는 언제나 환영합니다! 자유롭게 Pull Request를 제출해 주세요. 🎁
