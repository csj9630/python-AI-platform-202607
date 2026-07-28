import requests


def main() -> None:
    response = requests.get(
        "http://localhost:11434/api/tags",
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    models = data.get("models", [])

    print(f"설치 모델 수: {len(models)}")

    for model in models:
        print("-", model.get("name"))


if __name__ == "__main__":
    main()