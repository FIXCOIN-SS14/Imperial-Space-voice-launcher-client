import webview
import sys
import os
import ctypes
import gc

# Красивый темный интерфейс лаунчера
HTML_LAUNCHER = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #1e1e1e;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.6);
            text-align: center;
            width: 450px;
            border: 1px solid #333;
        }
        h2 { margin-top: 0; color: #ffcc00; font-size: 24px; }
        p { font-size: 14px; color: #aaaaaa; margin-bottom: 25px; }
        input {
            width: 90%;
            padding: 12px;
            margin-bottom: 20px;
            border: 1px solid #444;
            border-radius: 6px;
            background-color: #2b2b2b;
            color: #fff;
            font-size: 14px;
            outline: none;
        }
        input:focus { border-color: #ffcc00; }
        button {
            width: 100%;
            padding: 12px;
            background-color: #ffcc00;
            color: #000;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover { background-color: #e6b800; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Imperial Connect Voice</h2>
        <p>Вставьте ссылку на голосовой канал:</p>
        <input type="text" id="urlInput" placeholder="https://beta.imperialconnect.space/voice/client?..." autofocus>
        <button onclick="connect()">Подключиться</button>
    </div>
    <script>
        function connect() {
            var url = document.getElementById('urlInput').value;
            if (url && url.startsWith('http')) {
                // Меняем текущее окно на голосовой клиент
                window.location.href = url; 
            } else {
                alert('Пожалуйста, введите корректную ссылку (начиная с https://)');
            }
        }
        document.getElementById('urlInput').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') connect();
        });
    </script>
</body>
</html>
"""

def trim_memory():
    """Принудительно заставляет Windows выгрузить лишнюю ОЗУ"""
    if sys.platform == "win32":
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(handle)
        except Exception:
            pass
    gc.collect()

def on_loaded(window):
    """Вызывается при загрузке страницы"""
    # 1. Ставим приоритет процесса 'Ниже обычного' (чтобы не мешать играм, но звук не лагал)
    if sys.platform == "win32":
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            # 0x00004000 = BELOW_NORMAL_PRIORITY_CLASS
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000) 
        except Exception:
            pass

    # 2. Внедряем легкий CSS: убираем тяжелые тени и размытия (экономия ГПУ), 
    # но НЕ трогаем анимации, чтобы кнопки и микрофон работали корректно
    css_js = """
    const style = document.createElement('style');
    style.innerHTML = '* { box-shadow: none !important; text-shadow: none !important; backdrop-filter: none !important; }';
    document.head.appendChild(style);
    """
    window.evaluate_js(css_js)

    # 3. Чистим ОЗУ после загрузки
    trim_memory()

def main():
    # --- ОПТИМИЗАЦИЯ ДЛЯ WEBVIEW2 (БЕЗ ВРЕДА ДЛЯ ЗВУКА) ---
    if sys.platform == "win32":
        os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
            "--use-fake-ui-for-media-stream " # Авто-доступ к микрофону
            "--disable-background-networking " # Отключаем фоновые проверки
            "--disable-component-update "
            "--disable-sync "
            "--disable-translate "
            "--no-first-run "
            "--disable-smooth-scrolling "      # Отключаем плавный скролл (экономия ЦП)
            "--disk-cache-size=10485760"       # Ограничиваем кэш диска 10МБ
            # ВНИМАНИЕ: Мы НЕ отключаем ГПУ (--disable-gpu), чтобы не сломать WebRTC
        )

    window = webview.create_window(
        title="Imperial Connect Voice Launcher",
        html=HTML_LAUNCHER,
        width=600,
        height=500,
        min_size=(500, 400),
        text_select=True
    )

    # Привязываем оптимизацию к загрузке
    window.events.loaded += on_loaded

    webview.start(debug=False)

if __name__ == "__main__":
    main()