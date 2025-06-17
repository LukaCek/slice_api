from flask import Flask, render_template, request, send_file
import os
import re
import math
import subprocess
from pathlib import Path
import zipfile
import json
import xml.etree.ElementTree as ET


CENA_PLA_PLATIKE = 2 # cent/g
CENA_PETG_PLATIKE = 1.8 # cent/g

CENA_ELEKTRIKE = 20.002 # cent/kWh
PORABA_TISKALNIKA = 120 # Watts
VZDRZEVANJE_VSAKIH = 240*60 # ur * min v uri
CENA_VZDRZEVANJA = 30 # eur

def centi_v_evro_zaokrozi(centi):
    evri = centi / 100
    evri_zaokrozeni = math.ceil(evri * 100) / 100
    return f"{evri_zaokrozeni:.2f} €"

# Helper to convert '1h 16m 56s' → minutes (rounded up)
def time_to_minutes(timestr):
    h = m = s = 0
    if 'h' in timestr:
        h = int(re.search(r'(\d+)h', timestr).group(1))
    if 'm' in timestr:
        m = int(re.search(r'(\d+)m', timestr).group(1))
    if 's' in timestr:
        s = int(re.search(r'(\d+)s', timestr).group(1))
    total_minutes = h * 60 + m + math.ceil(s / 60)
    return total_minutes

def run_orcaslicer(input_file_path, quality):
    arrange = "1"
    orient = "1"
    while True:
        cmd = [
        "orcaslicer",
        "--arrange", arrange,
        "--orient", orient,
        "--export-slicedata", "./temp",
        "--load-settings", "printers/Bambu Lab P1S 0.4 nozzle.json;process/" + quality + " @BBL X1C.json",
        "--load-filaments", "test_data/filament.json",
        "--slice", "0",
        "--debug", "2",
        "--export-3mf", "./temp/output.3mf",
        "--info",
        "--pipe", "pipename",
        "temp/file.stl"
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            app.logger.info("OrcaSlicer STDOUT:\n%s", result.stdout)
            app.logger.info("OrcaSlicer STDERR:\n%s", result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            app.logger.error("OrcaSlicer failed with return code %s", e.returncode)
            app.logger.error("STDOUT:\n%s", e.stdout)
            app.logger.error("STDERR:\n%s", e.stderr)
        
        if arrange == "1" and orient == "1":
            app.logger.info("Attempting to slice again FIRST...")
            arrange = "0"
            orient = "1"
        elif arrange == "0" and orient == "1":
            app.logger.info("Attempting to slice again SECOND...")
            arrange = "1"
            orient = "0"
        elif arrange == "1" and orient == "0":
            app.logger.info("Attempting to slice again THIRD...")
            arrange = "0"
            orient = "0"
        else:
            return False


app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    # Get quontity profiles
    root_dir = Path('process/')

    # Recursively find all .json files
    json_files = root_dir.rglob('*.json')

    # Build dictionary: { "filename before @": "full path to .json" }
    json_dict = {}

    for file in json_files:
        # Get the filename without extension
        name = file.stem

        # Remove everything from '@' onwards
        clean_name = name.split('@')[0].strip()

        json_dict[clean_name] = str(file)

    return render_template("index.html", q=q, json_dict=json_dict)

@app.route("/price", methods=["POST"])
def price():
    app.logger.info("Received POST request to /price")
    global q
    if q >= 1:
        return f"Poskusi ponovno. Strežnik je zaseden. {q}"
    q += 1
    
    # Get the quality
    quality = request.form["quality"]
    output = request.form["output"]

    app.logger.info(f"Quality: {quality}")
    app.logger.info(f"Output: {output}")

    # Upload the file
    file = request.files["file"]
    file_path = os.path.join("temp/", "file.stl")
    file.save(file_path)
    app.logger.info(f"File saved to: {file_path}")

    # Run orcaslicer
    app.logger.info("Running orcaslicer...")
    if not run_orcaslicer(file_path, quality):
        app.logger.info("Slicing failed")
        for filename in os.listdir("temp/"):
            file_path = os.path.join("temp/", filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return f"Slicing failed <br> Quality: {quality}<br>q: {q}"
    app.logger.info("Slicing finished")

    # Check if slicing was successful
    app.logger.info("Checking if slicing was successful...")
    with open("result.json", "r") as f:
        result = f.read()
        app.logger.info(result)

        # extract error code
        parsed = json.loads(result)
        error_code = parsed.get("return_code")
        error_string = parsed.get("error_string")
        app.logger.info(f"Error code: {error_code}")
        if error_code:
            if error_code == -50:
                return f"Slicing was not successful <br> 3D model is too big."
            elif error_code == -100:
                return f"Slicing was not successful <br> 3D model is too small."
            else:
                return f"Slicing was not successful NEW ERROR<br> Error code: {error_code}<br> Error string: {error_string}"

        if "Success." not in result:
            app.logger.info("Slicing was not successful: " + result)
            return f"Slicing was not successful <br> {result}"
    
    # Wait for 3mf file to be generated
    app.logger.info("Waiting for 3mf file to be generated...")
    while not os.path.exists("temp/output.3mf"):
        print("Waiting for 3mf file to be generated...")
        pass
    
    # Extract .3mf file
    app.logger.info("Extracting .3mf file...")
    os.rename('temp/output.3mf', 'temp/output.zip')
    os.makedirs("temp/output", exist_ok=True)
    with zipfile.ZipFile("temp/output.zip", 'r') as zip_ref:
        zip_ref.extractall("temp/output")
    #os.remove("temp/output.zip")
    os.remove("temp/file.stl")

    ### Read slice info file ###
    app.logger.info("Reading sliced config file...")
    # So we can get filament usage info
    with open("temp/output/Metadata/slice_info.config", "r") as f:
        content = f.read()
    # Parse XML
    root = ET.fromstring(content)
    # Filament info
    filament = root.find("plate").find("filament")
    filament_data = {
    "type": filament.attrib.get("type"),
    "used_m": filament.attrib.get("used_m"),
    "used_g": filament.attrib.get("used_g")
    }
    app.logger.info(f"Filament: {filament_data}")

    # Get print time
    # Load G-code
    with open("temp/output/Metadata/plate_1.gcode", "r") as f:
        gcode = f.read()

    # Extract time and height
    model_time = re.search(r"model printing time:\s+([0-9hms\s]+);", gcode)
    total_time = re.search(r"total estimated time:\s+([0-9hms\s]+)", gcode)
    first_layer_time = re.search(r"first layer printing time.*?=\s+([0-9hms\s]+)", gcode)
    max_z = re.search(r"max_z_height:\s+([0-9.]+)", gcode)

    model_time_in_min = time_to_minutes(model_time.group(1))
    total_time_in_min = time_to_minutes(total_time.group(1))
    first_layer_time_in_min = time_to_minutes(first_layer_time.group(1))
    # Izračun cene
    if filament_data['type'] == "PLA":
        cena_materiala = CENA_PLA_PLATIKE * float(filament_data['used_g'])
    elif filament_data['type'] == "PETG":
        cena_materiala = CENA_PETG_PLATIKE * float(filament_data['used_g'])
    
    model_time_in_min = float(model_time_in_min)
    total_time_in_min = float(total_time_in_min)
    
    # Izračun cene
    cena_elektrike = CENA_ELEKTRIKE * (total_time_in_min/60) * PORABA_TISKALNIKA / (100 * 60)
    cena_vzdrzalnika = (CENA_VZDRZEVANJA / VZDRZEVANJE_VSAKIH) * model_time_in_min

    cena = cena_materiala + cena_elektrike + cena_vzdrzalnika

    # Pretvorba cen iz centov na evro
    cena_materiala = centi_v_evro_zaokrozi(cena_materiala)
    cena_elektrike = centi_v_evro_zaokrozi(cena_elektrike)
    cena_vzdrzalnika = centi_v_evro_zaokrozi(cena_vzdrzalnika)
    cena = centi_v_evro_zaokrozi(cena)

    # Zaokroži ceno na dve decimalke (zaorkroži navzgor)


    if output == "slicedata":
        return render_template("result.html", quality=quality, filament_data=filament_data, model_time=model_time.group(1), total_time=total_time.group(1), first_layer_time=first_layer_time.group(1), max_z=max_z.group(1), model_time_in_min=model_time_in_min, total_time_in_min=total_time_in_min, first_layer_time_in_min=first_layer_time_in_min, cena_materiala=cena_materiala, cena_elektrike=cena_elektrike, cena_vzdrzalnika=cena_vzdrzalnika, cena=cena)
    elif output == "3mf":
        return send_file("temp/output/output.3mf", as_attachment=True)
    elif output == "gcode":
        return gcode
    else:
        return send_file("temp/file.stl", as_attachment=True)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)