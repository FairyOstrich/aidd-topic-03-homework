import os
import sys
import subprocess
import time
import urllib.request
import webview


def start_django_process():
    """Запускает Django development server как отдельный процесс."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    return subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
        cwd=BASE_DIR,
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )


def wait_for_server(url, timeout=30):
    """Ждёт, пока сервер станет доступен."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)

    # Запускаем Django как отдельный процесс
    django_proc = start_django_process()

    try:
        # Ждём запуска сервера
        if not wait_for_server("http://127.0.0.1:8000/"):
            print("Сервер не запустился за отведённое время")
            django_proc.terminate()
            sys.exit(1)

        # Создаём десктопное окно (должно быть в основном потоке)
        window = webview.create_window(
            "Investing Demo — Мои инвестиции",
            "http://127.0.0.1:8000/",
            width=1200,
            height=800,
            resizable=True,
        )
        webview.start(debug=False)
    finally:
        # Останавливаем Django при закрытии окна
        django_proc.terminate()
        try:
            django_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            django_proc.kill()
