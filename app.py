from flask import Flask, request, jsonify, send_from_directory
from owlready2 import get_ontology
import os

app = Flask(__name__)

# Load ontology
ontology = get_ontology("SoilClassification.owl").load()

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
        print("Received Data:", data)  # Debug log (optional)

        # Parse data from form
        has_75Microns_retained = float(data['has_75Microns_retained'])
        has_4750Microns_retained = float(data['has_4750Microns_retained'])
        fines = float(data['fines'])
        cu = float(data['cu'])
        cc = float(data['cc'])
        liquid_limit = float(data['liquid_limit'])
        plastic_limit = float(data['plastic_limit'])
        color = data['color']

        # Calculations
        plasticity_index = liquid_limit - plastic_limit
        A_Line = 0.73 * (liquid_limit - 20)

        # Classification Logic
        if color.lower() == "dark":
            result = "Highly Organic Soil (PK)"
        elif has_75Microns_retained > 50:
            if has_4750Microns_retained > 50:
                if fines < 5:
                    if cu > 4 and 1 <= cc <= 3:
                        result = "Coarse-Grained Soil → Well-Graded Gravel"
                    else:
                        result = "Coarse-Grained Soil → Poorly-Graded Gravel"
                elif fines > 12:
                    if plasticity_index < 4:
                        result = "Coarse-Grained Soil → Silty Gravel"
                    elif plasticity_index > 7:
                        result = "Coarse-Grained Soil → Clayey Gravel"
                    else:
                        result = "Coarse-Grained Soil → Silty-Clayey Gravel (Dual Symbol)"
                else:
                    result = "Coarse-Grained Soil → Gravel with Fines (Dual Symbol)"
            else:
                if fines < 5:
                    if cu > 6 and 1 <= cc <= 3:
                        result = "Coarse-Grained Soil → Well-Graded Sand"
                    else:
                        result = "Coarse-Grained Soil → Poorly-Graded Sand"
                elif fines > 12:
                    if plasticity_index < A_Line:
                        result = "Coarse-Grained Soil → Silty Sand"
                    else:
                        result = "Coarse-Grained Soil → Clayey Sand"
                else:
                    result = "Coarse-Grained Soil → Sand with Fines (Dual Symbol)"
        elif has_75Microns_retained <= 50 and has_4750Microns_retained == 0:
            if fines > 50:
                if plasticity_index > A_Line:
                    fine_soil_type = "Clay"
                else:
                    fine_soil_type = "Silt"

                if liquid_limit < 35:
                    compressibility = "Low Compressible Soil"
                elif 35 <= liquid_limit <= 50:
                    compressibility = "Intermediate Compressible Soil"
                else:
                    compressibility = "High Compressible Soil"

                if liquid_limit > plastic_limit and liquid_limit != 0:
                    consistency_index = (liquid_limit - plastic_limit) / liquid_limit
                else:
                    consistency_index = 0

                result = (f"Fine-Grained Soil → {fine_soil_type} → {compressibility} "
                          f"→ Consistency Index: {round(consistency_index, 2)}")
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
    app.run(debug=True)
