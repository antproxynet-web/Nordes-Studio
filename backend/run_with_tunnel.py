from pyngrok import ngrok
import subprocess

# 1️⃣ Rodar o Flask (app.py)
subprocess.Popen(["python", "app.py"])

# 2️⃣ Abrir túnel na porta 5000
public_url = ngrok.connect(5000)
print("🚀 Túnel público:", public_url)
print("Abra esse link no navegador ou configure no Google OAuth")