from fastapi import FastAPI, HTTPException
from ollama import ResponseError, chat
from pydantic import BaseModel, Field


app = FastAPI()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
def create_chat(request: ChatRequest) -> ChatResponse:
    try:
        response = chat(
            model="gemma3:1b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 문서 AI 서비스의 친절한 도우미입니다."
                    ),
                },
                {
                    "role": "user",
                    "content": request.message,
                },
            ],
        )
    except ResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Local model error: {exc}",
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ollama server is unavailable.",
        ) from exc

    answer = response.message.content.strip()

    if not answer:
        raise HTTPException(
            status_code=502,
            detail="The local model returned an empty response.",
        )

    return ChatResponse(answer=answer)

'''

Code	Details
200	
Response body
Download
{
  "answer": "안녕하세요! 여러분을 최대한 자세하게 도와드릴 수 있도록 React를 설명 드리겠습니다.\n\n**React는 JavaScript 기반의 프론트는 렌더링 라이브러리**입니다.** 간단히 말해서, 웹페이지에서 어떻게 보이느냐 (UI)를 만드는 방법을 정의하는 도구라고 생각하면 됩니다. 마치 사진 편집기처럼 그림을 더 꾸밀 수 있게 해주는 소프트웨어랑 비슷하다고 할 수 있습니다.\n\n**React의 핵심 개념과 특징은 다음과 같습니다:**\n\n1.  **컴포넌트 기반:**\n    *   React는 **컴포넌트에 의존적인 웹 UI를 만드는데 집중합니다.** 이 컴포넌트는 개별적인 기능이나 화면 부분을 구성할 수 있는 단위입니다. \n    *   각 컴포넌트를 별로 분리해서 만들어 쓰면, 코드의 재사용성이 높아지고 유지보수가 용이해집니다. \n\n2.  **Virtual DOM (가상DOM):**\n     *   React는 웹페이지를 페이지처럼 생각하는 대신, Virtual DOM을 사용하여 실제 브라우저에 전달되는 데이터를 변경합니다.\n    *   컴퓨터에서 변경할 수 있는 데이터만 미리 계산해두고, 실제로 변경해야 하는 부분은 Virtual DOM의 변경 사항을 뒤로 보내고 다시 실제 Web Page를 생성해서 렌더링하는 과정을 반복합니다.  \n     *   이 과정이 빠르고 효율적으로 가능하게 하여 빠른 웹페이지 로딩 속도를 보장합니다.\n\n3. **JSX (JavaScript XML):**\n    * React는 JSX를 사용합니다. JSX는 JavaScript 코드를 HTML과 유사한 방식으로 렌더링할 수 있게 해주는 단어 배열입니다. \n    *   ```js\n        const element = (row => row . name);\n            ```\n\n    *  JSX는 인터랙션이나 사용자 입력에 따라 화면이 바뀌고 원하는 동작을 구현하는데 사용되는 중요한 도구입니다.\n\n\n\n\n4. **프로그래밍 래퍼:**\n    * React는 JavaScript를 사용하여 앱의 다양한 부분들을 렌더링하는 래퍼입니다. 즉, 특정 기능이나 UI의 구현 외에도 다른 로직 (예: API와 통신하거나 데이터 처리)을 관리합니다.\n\n**React의 주요 장점 및 용도 예시:**\n\n*   **반응형 웹 디자인:**  사용자 인터페이스에 대한 변화 속도에 따라 HTML 코드만 수정하면 되므로 화면이 최적화되고 사용자에게 편안한 경험을 제공할 수 있습니다 (예: 폰트 크기, 색상 변경 등).\n*   **리액티브 UI:** 리액티브는 JavaScript를 사용해서 UI 디자인을 구현하는 방식 중 하나입니다.  React는 React를 통해 리액티브 UI를 쉽게 만들 수 있게 합니다.\n\n* **트래킹(tracking) 효율적 시각화:** Google의  React Traces도 렌더링 과정에서 메모리 최적화 및 UI 렌더싱 과정을 분석할 수 있도록 도와주는 도구입니다.\n\n**어떤 종류에 있는 React에 대해 더 자세히 알고 싶으신가요? (예: Next, Remix 등)** 아니면 다른 질문이 있으시면 언제든지 물어가세요! 😊"
}
'''