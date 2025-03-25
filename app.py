from flask import Flask, request, jsonify, send_from_directory
from owlready2 import get_ontology
import os

app = Flask(__name__)

# Load ontology
ONTOLOGY_PATH = "SoilClassification.owl"
try:
    ontology = get_ontology(ONTOLOGY_PATH).load()
    print("Ontology loaded successfully.")
except Exception as e:
    print(f"Error loading ontology: {e}")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/styles.css')
def serve_css():
    return send_from_directory('.', 'styles.css')

@app.route('/classify', methods=['POST'])
def classify_soil():
    try:
        data = request.form  # 🔥 FIXED: Compatible with FormData
        print("Received Data:", data)  # Debugging log

        # Parse data from form
        has_75Microns_retained = float(data.get('has_75Microns_retained', 0))
        has_4750Microns_retained = float(data.get('has_4750Microns_retained', 0))
        fines = float(data.get('fines', 0))
        cu = float(data.get('cu', 0))
        cc = float(data.get('cc', 0))
        liquid_limit = float(data.get('liquid_limit', 0))
        plastic_limit = float(data.get('plastic_limit', 0))
        color = data.get('color', '').strip().lower()

        # Calculations
        plasticity_index = max(0, liquid_limit - plastic_limit)  # Prevent negative values
        A_Line = 0.73 * (liquid_limit - 20)

        # Classification Logic
        if color == "dark":
            result = "Highly Organic Soil (PK)"
        elif has_75Microns_retained > 50:
            if has_4750Microns_retained > 50:
                if fines < 5:
                    result = "Well-Graded Gravel" if (cu > 4 and 1 <= cc <= 3) else "Poorly-Graded Gravel"
                elif fines > 12:
                    if plasticity_index < 4:
                        result = "Silty Gravel"
                    elif plasticity_index > 7:
                        result = "Clayey Gravel"
                    else:
                        result = "Silty-Clayey Gravel (Dual Symbol)"
                else:
                    result = "Gravel with Fines (Dual Symbol)"
            else:
                if fines < 5:
                    result = "Well-Graded Sand" if (cu > 6 and 1 <= cc <= 3) else "Poorly-Graded Sand"
                elif fines > 12:
                    result = "Silty Sand" if plasticity_index < A_Line else "Clayey Sand"
                else:
                    result = "Sand with Fines (Dual Symbol)"
        elif has_75Microns_retained <= 50 and has_4750Microns_retained == 0:
            if fines > 50:
                fine_soil_type = "Clay" if plasticity_index > A_Line else "Silt"

                if liquid_limit < 35:
                    compressibility = "Low Compressible Soil"
                elif 35 <= liquid_limit <= 50:
                    compressibility = "Intermediate Compressible Soil"
                else:
                    compressibility = "High Compressible Soil"

                consistency_index = max(0, (liquid_limit - plastic_limit) / liquid_limit) if liquid_limit > 0 else 0

                result = f"Fine-Grained Soil → {fine_soil_type} → {compressibility} → Consistency Index: {round(consistency_index, 2)}"
            else:
                result = "Unknown Fine-Grained Soil Type"
        else:
            result = "Unknown Soil Type"

        return jsonify({
            'classification': result,
            'pi': round(plasticity_index, 2),
            'aline': round(A_Line, 2)
        })

    except Exception as e:
        print("Error in classification:", e)
        return jsonify({'error': 'Server Error: Unable to classify soil.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Auto-detect port for hosting
    app.run(host="0.0.0.0", port=port, debug=True)
