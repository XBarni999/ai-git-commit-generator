import os
import subprocess
import sys
import requests

# Налаштування локальної моделі через Ollama (можна змінити на OpenAI або інший API)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # або mistral, qwen2.5 тощо

def get_git_diff():
    try:
        # Отримуємо змінені рядки, які готові до коміту (staged)
        result = subprocess.run(
            ["git", "diff", "--cached"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        print("Помилка: Переконайтеся, що ви знаходитесь у git-репозиторії.")
        sys.exit(1)

def generate_commit_message(diff):
    if not diff.strip():
        return "Немає змін для коміту. Додайте файли через 'git add'."

    prompt = (
        "Напиши коротке, але інформативне повідомлення для git commit на основі цього diff. "
        "Використовуй стандарт Conventional Commits (наприклад: feat: add login feature, fix: resolve crash). "
        "Повідомлення має бути англійською мовою, лаконічним і в один рядок. "
        f"Ось зміни:\n\n{diff}"
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException:
        return "Помилка зв'язку з локальним ШІ. Перевірте, чи запущена Ollama."

def main():
    print("Аналіз змін у репозиторії...")
    diff = get_git_diff()
    
    if not diff.strip():
        print("Нічого не змінено. Спочатку виконайте 'git add'.")
        return

    print("Генерація повідомлення за допомогою ШІ...")
    commit_message = generate_commit_message(diff)
    
    print("\nРекомендований коміт-меседж:")
    print("-" * 40)
    print(commit_message)
    print("-" * 40)

if __name__ == "__main__":
    main()