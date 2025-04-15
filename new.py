from flask import Flask, render_template, request, jsonify,redirect, url_for,abort
import subprocess,psutil

app = Flask(__name__)

# Routes for different home pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/homea')
def homea():
    return render_template('homea.html')

@app.route('/homes')
def homes():
    return render_template('homes.html')

@app.route('/homed')
def homed():
    return render_template('homed.html')

@app.route('/homec')
def homec():
    return render_template('homec.html')

# Routes for virtual tools pages
@app.route('/virtualkeyboard')
def virtual_keyboard():
    return render_template('virtualkeyboard.html')

@app.route('/virtualmouse')
def virtual_mouse():
    return render_template('virtualmouse.html')

@app.route('/virtualcanvas')
def virtual_canvas():
    return render_template('virtualcanvas.html')

@app.route('/virtualcalculator')
def virtual_calculator():
    return render_template('virtualcalculator.html')

# Additional routes
@app.route('/vka')
def vka():
    return render_template('vka.html')

@app.route('/vks')
def vks():
    return render_template('vks.html')

@app.route('/vkd')
def vkd():
    return render_template('vkd.html')

@app.route('/vma')
def vma():
    return render_template('vma.html')

@app.route('/vms')
def vms():
    return render_template('vms.html')

@app.route('/vmd')
def vmd():
    return render_template('vmd.html')

@app.route('/vcaa')
def vcaa():
    return render_template('vcaa.html')

@app.route('/vcas')
def vcas():
    return render_template('vcas.html')

@app.route('/vcad')
def vcad():
    return render_template('vcad.html')

@app.route('/vca')
def vca():
    return render_template('vca.html')

@app.route('/vcs')
def vcs():
    return render_template('vcs.html')

@app.route('/vcd')
def vcd():
    return render_template('vcd.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/try_virtual_canvas")
def try_virtual_canvas():
    subprocess.Popen(["streamlit", "run", "Virtual_Canvas.py", "--server.port", "8504"])
    return redirect(f"http://127.0.0.1:8504")

@app.route("/try_virtual_keyboard")
def try_virtual_keyboard():
    subprocess.Popen(["streamlit", "run", "Virtual_Keyboard.py", "--server.port", "8503"])
    return redirect(f"http://127.0.0.1:8503")

@app.route("/try_proton")
def try_proton():
    subprocess.Popen(["python", "Proton.py"])
    return redirect(f"http://127.0.0.1:5005")

@app.route("/try_virtual_calculator")
def try_virtual_calculator():
    subprocess.Popen(["streamlit", "run", "Virtual_Calculator.py", "--server.port", "8506"])
    return redirect("http://127.0.0.1:8506")


if __name__ == '__main__':
    app.run(debug=True)