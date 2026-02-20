import os, shutil, subprocess, time, random, sys, traceback

def project_root():
    # quando vira EXE, sys.executable aponta pro .exe em dist/
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

ROOT = project_root()
LOG = os.path.join(ROOT, "restart.log")

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

try:
    os.chdir(ROOT)
    log("=== RESTART START ===")
    log(f"ROOT={ROOT}")

    # 1) parar Flask na porta 5000 (sem matar todos os python.exe)
    r = run('for /f "tokens=5" %a in (\'netstat -aon ^| findstr ":5000"\') do @echo %a')
    pids = sorted(set([p.strip() for p in r.stdout.splitlines() if p.strip().isdigit()]))

    log("PIDs on :5000 => " + (", ".join(pids) if pids else "none"))

    for pid in pids:
        run(f"taskkill /F /PID {pid}")

    # 2) limpar cache python
    for base, dirs, files in os.walk(ROOT):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(base, d), ignore_errors=True)
        for f in files:
            if f.endswith(".pyc"):
                try:
                    os.remove(os.path.join(base, f))
                except:
                    pass
    log("Cache limpo.")

    # 3) iniciar flask
    app_py = os.path.join(ROOT, "app.py")
    if not os.path.exists(app_py):
        raise FileNotFoundError(f"Não achei app.py em: {app_py}")

    py = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
    if not os.path.exists(py):
        py = "python"

    subprocess.Popen([py, "app.py"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("Flask iniciado.")
    time.sleep(1.0)

    # 4) abrir Chrome sem cache (perfil temporário)
    tmp_profile = os.path.join(os.environ.get("TEMP", ROOT), "flask_nocache_profile")
    shutil.rmtree(tmp_profile, ignore_errors=True)

    chrome = os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"),
                          r"Google\Chrome\Application\chrome.exe")

    url = f"http://127.0.0.1:5000/?v={random.randint(100000,999999)}"
    log("Abrindo URL: " + url)

    if os.path.exists(chrome):
        subprocess.Popen([chrome,
                          f"--user-data-dir={tmp_profile}",
                          "--disable-application-cache",
                          "--disk-cache-size=1",
                          url])
        log("Chrome OK.")
    else:
        run(f'start "" "{url}"')
        log("Chrome não encontrado, abri no padrão.")

    log("=== RESTART OK ===")

except Exception:
    log("=== RESTART ERROR ===")
    log(traceback.format_exc())