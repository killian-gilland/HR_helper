# Fichier : src/modules/ui_components.py
import plotly.graph_objects as go

def create_radar_chart(res):
    """Génère le graphique radar des compétences."""
    categories = ['Cœur Tech', 'Outils', 'Impact', 'Séniorité', 'Soft Skills', 'Clarté/Récit']
    values = [
        (res.get('n_coeur', 0) / 65) * 100, 
        (res.get('n_outils', 0) / 10) * 100, 
        (res.get('n_imp', 0) / 10) * 100, 
        (res.get('n_sen', 0) / 5) * 100, 
        (res.get('n_soft', 0) / 5) * 100, 
        (res.get('n_story', 0) / 5) * 100
    ]
    values.append(values[0])
    categories_closed = categories + [categories[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, 
        theta=categories_closed, 
        fill='toself', 
        fillcolor='rgba(59, 130, 246, 0.2)', 
        line=dict(color='#3B82F6', width=2), 
        name=res.get('nom', 'Candidat')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)), 
        showlegend=False, 
        margin=dict(l=30, r=30, t=20, b=20), 
        height=250, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def make_progress_bar(label, value, max_val, color_hex="#3B82F6"):
    """Génère une barre de progression HTML personnalisée."""
    percent = (value / max_val) * 100
    return f"""
    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; color: #475569; margin-top: 6px;">
        <span>{label}</span><span>{value}/{max_val}</span>
    </div>
    <div class="meter-container">
        <div class="meter-fill" style="width: {percent}%; background-color: {color_hex};"></div>
    </div>
    """