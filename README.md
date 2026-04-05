# Gemini 및 OpenAI 모델을 위한 Anthropic API 프록시 🔄

**Claude Code와 같은 Anthropic 클라이언트를 Gemini, OpenAI 또는 직접적인 Anthropic 백엔드와 함께 사용하세요.** 🤝

Anthropic 클라이언트를 Gemini, OpenAI 또는 Anthropic 모델 자체(일종의 투명 프록시)와 함께 사용할 수 있게 해주는 프록시 서버입니다. 모든 과정은 LiteLLM을 통해 이루어집니다. 🌉


![Anthropic API 프록시](pic.png)

## 빠른 시작 ⚡

### 사전 요구 사항

- OpenAI API 키 🔑
- Google AI Studio (Gemini) API 키 (Google 제공자를 사용하는 경우) 🔑
- Vertex AI API가 활성화된 Google Cloud 프로젝트 (Gemini에 애플리케이션 기본 자격 증명을 사용하는 경우) ☁️
- [uv](https://github.com/astral-sh/uv) 설치됨.

### 설정 🛠️

#### 소스에서 설치

1. **저장소 복제**:
   ```bash
   git clone https://github.com/1rgs/claude-code-proxy.git
   cd claude-code-proxy
   ```

2. **uv 설치** (아직 설치하지 않은 경우):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   *(`uv`는 서버를 실행할 때 `pyproject.toml`을 기반으로 의존성을 처리합니다)*

3. **환경 변수 설정**:
   예시 환경 파일을 복사합니다:
   ```bash
   cp .env.example .env
   ```
   `.env` 파일을 편집하여 API 키와 모델 설정을 입력합니다:

   *   `ANTHROPIC_API_KEY`: (선택 사항) Anthropic 모델로 프록시하는 경우에만 필요합니다.
   *   `OPENAI_API_KEY`: OpenAI API 키 (기본 OpenAI 설정을 사용하거나 폴백용으로 필요).
   *   `GEMINI_API_KEY`: Google AI Studio (Gemini) API 키 (`PREFERRED_PROVIDER=google` 및 `USE_VERTEX_AUTH=false`인 경우 필요).
   *   `USE_VERTEX_AUTH` (선택 사항): 애플리케이션 기본 자격 증명(ADC)을 사용하려면 `true`로 설정합니다 (정적 API 키가 필요하지 않음). 주의: `USE_VERTEX_AUTH=true`일 때 `VERTEX_PROJECT`와 `VERTEX_LOCATION`을 설정해야 합니다.
   *   `VERTEX_PROJECT` (선택 사항): Google Cloud 프로젝트 ID (`PREFERRED_PROVIDER=google` 및 `USE_VERTEX_AUTH=true`인 경우 필요).
   *   `VERTEX_LOCATION` (선택 사항): Vertex AI를 위한 Google Cloud 리전 (예: `us-central1`) (`PREFERRED_PROVIDER=google` 및 `USE_VERTEX_AUTH=true`인 경우 필요).
   *   `PREFERRED_PROVIDER` (선택 사항): `openai` (기본값), `google`, 또는 `anthropic`으로 설정합니다. 이는 `haiku`/`sonnet` 매핑을 위한 기본 백엔드를 결정합니다.
   *   `BIG_MODEL` (선택 사항): `sonnet` 요청을 매핑할 모델입니다. 기본값은 `gpt-4.5-preview` (`PREFERRED_PROVIDER=openai`인 경우) 또는 `gemini-2.0-pro-exp-02-05`입니다. `PREFERRED_PROVIDER=anthropic`일 때는 무시됩니다.
   *   `SMALL_MODEL` (선택 사항): `haiku` 요청을 매핑할 모델입니다. 기본값은 `gpt-4o-mini` (`PREFERRED_PROVIDER=openai`인 경우) 또는 `gemini-2.0-flash`입니다. `PREFERRED_PROVIDER=anthropic`일 때는 무시됩니다.

   **매핑 로직:**
   - `PREFERRED_PROVIDER=openai` (기본값)인 경우, `haiku`/`sonnet`은 `openai/` 접두사가 붙은 `SMALL_MODEL`/`BIG_MODEL`로 매핑됩니다.
   - `PREFERRED_PROVIDER=google`인 경우, `haiku`/`sonnet`은 해당 모델이 서버의 알려진 `GEMINI_MODELS` 목록에 있는 경우 `gemini/` 접두사가 붙은 `SMALL_MODEL`/`BIG_MODEL`로 매핑됩니다 (그렇지 않으면 OpenAI 매핑으로 대체됨).
   - `PREFERRED_PROVIDER=anthropic`인 경우, `haiku`/`sonnet` 요청은 다른 모델로 재매핑되지 않고 `anthropic/` 접두사와 함께 Anthropic으로 직접 전달됩니다.

4. **서버 실행**:
   ```bash
   uv run uvicorn server:app --host 0.0.0.0 --port 8082 --reload
   ```
   *(`--reload`는 개발용 선택 사항입니다)*

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

프록시는 설정된 모델에 따라 Claude 모델을 OpenAI 또는 Gemini 모델로 자동으로 매핑합니다:

| Claude 모델 | 기본 매핑 | BIG_MODEL/SMALL_MODEL이 Gemini 모델일 때 |
|--------------|--------------|---------------------------|
| haiku | openai/gpt-4o-mini | gemini/[모델명] |
| sonnet | openai/gpt-4o | gemini/[모델명] |

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
