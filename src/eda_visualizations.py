import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def plot_age_distribution(df_patients, theme_colors):
    """Interactive Age Distribution histogram."""
    df = df_patients.copy()
    df['BIRTHDATE'] = pd.to_datetime(df['BIRTHDATE'])
    df['Age'] = 2026 - df['BIRTHDATE'].dt.year
    
    fig = px.histogram(
        df, x="Age", nbins=20, 
        title="Patient Age Distribution",
        color_discrete_sequence=[theme_colors['primary']],
        template="plotly_white"
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Age (Years)",
        yaxis_title="Count"
    )
    return fig

def plot_gender_breakdown(df_patients, theme_colors):
    """Interactive Gender Pie Chart."""
    counts = df_patients['GENDER'].value_counts()
    fig = px.pie(
        values=counts.values, 
        names=counts.index, 
        title="Gender Breakdown",
        color_discrete_sequence=[theme_colors['primary'], theme_colors['secondary']],
        template="plotly_white",
        hole=0.4
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_top_conditions(df_conditions, theme_colors):
    """Interactive bar chart of clinical conditions."""
    top_c = df_conditions['DESCRIPTION'].value_counts().head(10).reset_index()
    top_c.columns = ['Condition', 'Count']
    
    fig = px.bar(
        top_c, y='Condition', x='Count', 
        orientation='h',
        title="Top 10 Clinical Conditions",
        color_discrete_sequence=[theme_colors['accent']],
        template="plotly_white"
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis={'categoryorder':'total ascending'}
    )
    return fig

def plot_expense_analysis(df_patients, theme_colors):
    """Scatter plot of Healthcare Expenses vs Coverage."""
    fig = px.scatter(
        df_patients, 
        x="HEALTHCARE_COVERAGE", 
        y="HEALTHCARE_EXPENSES",
        color="GENDER",
        title="Coverage vs. Expenses Analysis",
        color_discrete_map={'M': theme_colors['primary'], 'F': theme_colors['accent']},
        template="plotly_white",
        hover_data=['FIRST', 'LAST']
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_individual_vitals(vitals_dict, theme_colors):
    """Radar chart for individual patient vitals."""
    categories = ['Temp', 'SpO2', 'BP(S)', 'BP(D)', 'HR']
    # Normalize values for visualization purposes
    values = [
        vitals_dict.get('Temperature', 37)/40,
        vitals_dict.get('SpO2', 98)/100,
        vitals_dict.get('SystolicBloodPressure', 120)/180,
        vitals_dict.get('DiastolicBloodPressure', 80)/120,
        vitals_dict.get('Heartrate', 70)/120
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Patient Vitals',
        line_color=theme_colors['primary']
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        title="Multimodal Vital Profile",
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig
