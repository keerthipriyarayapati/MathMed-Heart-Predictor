import gradio as gr
import numpy as np
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px

model = joblib.load("heart_disease_rf_model.pkl")
scaler = joblib.load("scaler.pkl")

css = """
body{
    background:#f4f8fb;
}

.gradio-container{
    max-width:1400px !important;
}

.header{
    background:linear-gradient(135deg,#0F4C81,#1E88E5);
    padding:25px;
    border-radius:15px;
    color:white;
    text-align:center;
    margin-bottom:15px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.15);
}

.metric-card{
    background:white;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 3px 12px rgba(0,0,0,0.12);
    text-align:center;
}

.footer{
    text-align:center;
    padding:20px;
    color:#555;
}
"""

def patient_metrics_chart(age, bp, chol, hr):

    fig = px.bar(
        x=["Age","Blood Pressure","Cholesterol","Heart Rate"],
        y=[age,bp,chol,hr],
        title="Patient Health Metrics"
    )

    fig.update_layout(
        height=400,
        template="plotly_white"
    )

    return fig


def math_features_chart(bp_ratio, age_bp, flow):

    fig = px.bar(
        x=[
            "BP/Chol Ratio",
            "Age-BP Index",
            "Flow Magnitude"
        ],
        y=[
            bp_ratio*100,
            age_bp/100,
            flow
        ],
        title="Mathematical Feature Analysis"
    )

    fig.update_layout(
        height=400,
        template="plotly_white"
    )

    return fig


def confidence_gauge(confidence):

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=confidence,
            title={"text":"Prediction Confidence (%)"},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"#1E88E5"},
                "steps":[
                    {"range":[0,50],"color":"#ffebee"},
                    {"range":[50,75],"color":"#fff3e0"},
                    {"range":[75,100],"color":"#e8f5e9"}
                ]
            }
        )
    )

    fig.update_layout(height=350)

    return fig


def radar_chart(age, bp, chol, hr, flow):

    categories = [
        "Age",
        "BP",
        "Cholesterol",
        "Heart Rate",
        "Flow Magnitude"
    ]

    values = [
        age/77,
        bp/200,
        chol/600,
        hr/220,
        flow/300
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name="Patient Profile"
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        showlegend=False,
        title="Cardiovascular Radar Analysis",
        height=450
    )

    return fig

def predict_heart_disease(
    cp,
    thalach,
    slope,
    age,
    trestbps,
    chol,
    oldpeak,
    exang,
    ca,
    thal
):

    # Mathematical Features

    bp_chol_ratio = trestbps / chol
    age_bp_index = age * trestbps
    flow_magnitude = np.sqrt(
        (trestbps ** 2) +
        (thalach ** 2)
    )

    features = [[
        cp,
        thalach,
        slope,
        age,
        trestbps,
        chol,
        oldpeak,
        exang,
        ca,
        thal,
        bp_chol_ratio,
        age_bp_index,
        flow_magnitude
    ]]

    scaled_features = scaler.transform(features)

    prediction = model.predict(
        scaled_features
    )[0]

    probability = model.predict_proba(
        scaled_features
    )[0]

    confidence = round(
        max(probability) * 100,
        2
    )

    risk_probability = round(
        probability[1] * 100,
        2
    )

    if prediction == 1:

        result_card = f"""
        <div class='metric-card'
        style='border-left:8px solid #e53935;'>

        <h2>⚠️ HIGH RISK</h2>

        <h3>
        Heart Disease Likely
        </h3>

        <h2>
        {risk_probability:.2f}%
        </h2>

        </div>
        """

    else:

        result_card = f"""
        <div class='metric-card'
        style='border-left:8px solid #43a047;'>

        <h2>✅ LOW RISK</h2>

        <h3>
        Heart Disease Unlikely
        </h3>

        <h2>
        {100-risk_probability:.2f}%
        </h2>

        </div>
        """

    metrics_html = f"""
    <div class='metric-card'>

    <h3>Flow Magnitude</h3>

    <h2>{flow_magnitude:.2f}</h2>

    <hr>

    <h3>BP / Chol Ratio</h3>

    <h2>{bp_chol_ratio:.3f}</h2>

    <hr>

    <h3>Age-BP Index</h3>

    <h2>{age_bp_index:.2f}</h2>

    <hr>

    <h3>Confidence</h3>

    <h2>{confidence}%</h2>

    </div>
    """

    patient_chart = patient_metrics_chart(
        age,
        trestbps,
        chol,
        thalach
    )

    math_chart = math_features_chart(
        bp_chol_ratio,
        age_bp_index,
        flow_magnitude
    )

    gauge_chart = confidence_gauge(
        confidence
    )

    radar = radar_chart(
        age,
        trestbps,
        chol,
        thalach,
        flow_magnitude
    )

    # =====================
    # ABOUT ANALYSIS
    # =====================

    analysis_text = f"""
### Mathematical Analysis

**Flow Magnitude:** {flow_magnitude:.2f}

Represents the combined cardiovascular flow intensity derived using vector magnitude principles.

**BP/Chol Ratio:** {bp_chol_ratio:.3f}

Measures the relationship between blood pressure and cholesterol.

**Age-BP Index:** {age_bp_index:.2f}

Combines age and blood pressure into a composite cardiovascular indicator.

### Prediction Summary

Predicted Heart Disease Risk: **{risk_probability:.2f}%**

Model Confidence: **{confidence}%**
"""

    return (
        result_card,
        metrics_html,
        analysis_text,
        patient_chart,
        math_chart,
        gauge_chart,
        radar
    )

with gr.Blocks(
    css=css,
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="cyan"
    ),
    title="MathMed Heart Predictor"
) as demo:

    gr.HTML("""
    <div class="header">

    <h1>🫀 MathMed Heart Predictor</h1>

    <h3>
    Integrating Mathematics and Medicine for Intelligent Heart Disease Risk Assessment
    </h3>

    <p>
    AI-Powered Cardiovascular Analytics Dashboard using Mathematical Modeling, Data Analytics and Machine Learning
    </p>

    </div>
    """)

    with gr.Tabs():

        with gr.Tab("🏠 Prediction"):

            with gr.Row():

                with gr.Column():

                    gr.Markdown("## 👤 Patient Information")

                    age = gr.Slider(
                        29,
                        77,
                        value=53,
                        step=1,
                        label="Age"
                    )

                    trestbps = gr.Slider(
                        90,
                        200,
                        value=145,
                        step=1,
                        label="Resting Blood Pressure"
                    )

                    chol = gr.Slider(
                        100,
                        600,
                        value=350,
                        step=1,
                        label="Cholesterol"
                    )

                    thalach = gr.Slider(
                        70,
                        220,
                        value=145,
                        step=1,
                        label="Maximum Heart Rate"
                    )

                    oldpeak = gr.Slider(
                        0.0,
                        6.5,
                        value=1.0,
                        step=0.1,
                        label="Oldpeak"
                    )

                with gr.Column():

                    gr.Markdown("## 🫀 Clinical Parameters")

                    cp = gr.Dropdown(
                        [0, 1, 2, 3],
                        value=2,
                        label="Chest Pain Type"
                    )

                    exang = gr.Dropdown(
                        [0, 1],
                        value=0,
                        label="Exercise Induced Angina"
                    )

                    slope = gr.Dropdown(
                        [0, 1, 2],
                        value=1,
                        label="Slope"
                    )

                    ca = gr.Dropdown(
                        [0, 1, 2, 3, 4],
                        value=0,
                        label="Major Vessels"
                    )

                    thal = gr.Dropdown(
                        [0, 1, 2, 3],
                        value=2,
                        label="Thal"
                    )

            predict_btn = gr.Button(
                "🔍 Predict Heart Disease Risk",
                variant="primary"
            )

            result_output = gr.HTML()

            metric_output = gr.HTML()

            analysis_output = gr.Markdown()

        with gr.Tab("📊 Analytics Dashboard"):

            patient_chart_output = gr.Plot(
                label="Patient Metrics"
            )

            with gr.Row():

                math_chart_output = gr.Plot(
                    label="Mathematical Features"
                )

                gauge_chart_output = gr.Plot(
                    label="Confidence Gauge"
                )

            radar_chart_output = gr.Plot(
                label="Radar Analysis"
            )


        with gr.Tab("ℹ️ About Project"):

            gr.Markdown("""

# MathMed Heart Predictor

An AI-powered healthcare application that integrates
Mathematics, Data Analytics, and Machine Learning
for Heart Disease Risk Prediction.

## Project Architecture

### Phase 1 — Mathematical Modeling

Vector calculus inspired cardiovascular indicators:

- Flow Magnitude
- BP/Chol Ratio
- Age-BP Index

### Phase 2 — Data Analytics

Heart Disease Dataset Analysis

### Phase 3 — Machine Learning

Algorithms Used:

- Logistic Regression
- Random Forest Classifier

### Model Performance

- Logistic Regression Accuracy: 80.33%
- Random Forest Accuracy: 93.44%

### Features

✅ Mathematical Feature Engineering

✅ Machine Learning Prediction

✅ Interactive Analytics Dashboard

✅ Cardiovascular Risk Assessment

---

""")

    predict_btn.click(
        fn=predict_heart_disease,
        inputs=[
            cp,
            thalach,
            slope,
            age,
            trestbps,
            chol,
            oldpeak,
            exang,
            ca,
            thal
        ],
        outputs=[
            result_output,
            metric_output,
            analysis_output,
            patient_chart_output,
            math_chart_output,
            gauge_chart_output,
            radar_chart_output
        ]
    )

    gr.HTML("""
    <div class="footer">

    <hr>

    <h3>MathMed Heart Predictor</h3>

    <p>
    Integrating Mathematics and Medicine for Intelligent Heart Disease Prediction
    </p>

    <p>
    Random Forest Accuracy: 93.44%
    </p>

    </div>
    """)

demo.launch()
