import streamlit as st
import pandas as pd
from datetime import datetime
import json
import traceback

# Set page config FIRST
st.set_page_config(
    page_title="Khisba GIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import Plotly with error handling
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError as e:
    PLOTLY_AVAILABLE = False
    st.error(f"❌ Plotly import failed: {str(e)}")
    st.info("Please add 'plotly>=5.17.0' to requirements.txt")

# Custom CSS for Clean Green & Black Theme
st.markdown("""
<style>
    /* Base styling */
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    
    /* Remove Streamlit default padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Green & Black Theme */
    :root {
        --primary-green: #00ff88;
        --accent-green: #00cc6a;
        --primary-black: #000000;
        --card-black: #0a0a0a;
        --secondary-black: #111111;
        --border-gray: #222222;
        --text-white: #ffffff;
        --text-gray: #999999;
        --text-light-gray: #cccccc;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--text-white) !important;
    }
    
    h1 {
        font-size: 2rem !important;
        background: linear-gradient(90deg, var(--primary-green), var(--accent-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }
    
    /* Cards */
    .card {
        background: var(--card-black);
        border: 1px solid var(--border-gray);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: var(--primary-green);
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, var(--primary-green), var(--accent-green));
        color: var(--primary-black) !important;
        border: none;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        margin: 5px 0;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        background: rgba(0, 255, 136, 0.1);
        color: var(--primary-green);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-gray), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_area' not in st.session_state:
    st.session_state.selected_area = None

# Authentication check
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="card" style="margin: 100px 0; text-align: center;">
            <h1 style="text-align: center;">🌍 KHISBA GIS</h1>
            <p style="color: #999999; margin-bottom: 30px;">3D Global Vegetation Analytics</p>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <span class="status-badge">🔐 Authentication Required</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("", type="password", placeholder="Enter admin password", label_visibility="collapsed")
        
        if st.button("🔓 Sign In", type="primary", use_container_width=True):
            if password == "admin":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid password")
    
    st.markdown("""
    <div style="text-align: center; color: #666666; font-size: 12px; padding: 20px;">
        <p>Demo Access: Use <strong>admin</strong> / <strong>admin</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Main Dashboard
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div>
        <h1>🌍 KHISBA GIS</h1>
        <p style="color: #999999; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation Analytics</p>
    </div>
    <div style="display: flex; gap: 10px;">
        <span class="status-badge">Online</span>
        <span class="status-badge">v2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Create main layout
col1, col2 = st.columns([0.3, 0.7], gap="large")

# LEFT SIDEBAR - Controls
with col1:
    # Area Selection Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin: 0 0 15px 0;">📍 Area Selection</h3>', unsafe_allow_html=True)
    
    # Country selection
    countries = ["Select a country", "United States", "Canada", "United Kingdom", "Germany", "France", "Australia", "India", "Brazil", "South Africa", "Kenya"]
    selected_country = st.selectbox(
        "Country",
        options=countries,
        index=0,
        help="Choose a country for analysis"
    )
    
    if selected_country and selected_country != "Select a country":
        # Region selection
        regions = {
            "United States": ["California", "Texas", "Florida", "New York", "Colorado"],
            "Canada": ["Ontario", "Quebec", "British Columbia", "Alberta"],
            "United Kingdom": ["England", "Scotland", "Wales", "Northern Ireland"],
            "Germany": ["Bavaria", "Berlin", "Hamburg", "North Rhine-Westphalia"],
            "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia"]
        }
        
        region_options = regions.get(selected_country, ["All regions"])
        selected_region = st.selectbox(
            "State/Province",
            options=["Select region"] + region_options,
            index=0
        )
        
        # Store selected area
        if selected_region and selected_region != "Select region":
            st.session_state.selected_area = f"{selected_region}, {selected_country}"
        else:
            st.session_state.selected_area = selected_country
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis Settings Card
    if st.session_state.selected_area:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin: 0 0 15px 0;">⚙️ Analysis Settings</h3>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2023, 1, 1),
                help="Start date for analysis"
            )
        with col_b:
            end_date = st.date_input(
                "End Date",
                value=datetime(2023, 12, 31),
                help="End date for analysis"
            )
        
        collection_choice = st.selectbox(
            "Satellite Source",
            options=["Sentinel-2", "Landsat-8", "MODIS"],
            help="Choose satellite collection"
        )
        
        cloud_cover = st.slider(
            "Max Cloud Cover (%)",
            min_value=0,
            max_value=100,
            value=20,
            help="Maximum cloud cover percentage"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Vegetation Indices Card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin: 0 0 15px 0;">🌿 Vegetation Indices</h3>', unsafe_allow_html=True)
        
        available_indices = ['NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 'MSAVI', 'ARVI']
        selected_indices = st.multiselect(
            "Select Indices",
            options=available_indices,
            default=['NDVI', 'EVI', 'SAVI'],
            help="Choose vegetation indices to analyze"
        )
        
        # Run Analysis Button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True, key="run_analysis"):
            if not selected_indices:
                st.error("Please select at least one vegetation index")
            else:
                with st.spinner("Generating analysis data..."):
                    try:
                        # Generate realistic demo data
                        import numpy as np
                        
                        # Create date range
                        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
                        
                        # Generate different patterns for each index
                        results = {}
                        for idx, index in enumerate(selected_indices):
                            # Create seasonal pattern with some noise
                            n_days = len(date_range)
                            base_pattern = np.sin(2 * np.pi * np.arange(n_days) / 365) * 0.3 + 0.5
                            
                            # Add index-specific variations
                            if index == 'NDVI':
                                values = base_pattern + np.random.normal(0, 0.05, n_days) + 0.1
                            elif index == 'EVI':
                                values = base_pattern * 0.8 + np.random.normal(0, 0.04, n_days) + 0.15
                            elif index == 'SAVI':
                                values = base_pattern * 0.9 + np.random.normal(0, 0.03, n_days) + 0.2
                            elif index == 'NDWI':
                                values = np.sin(2 * np.pi * np.arange(n_days) / 180) * 0.2 + 0.3 + np.random.normal(0, 0.04, n_days)
                            else:
                                values = base_pattern + np.random.normal(0, 0.03, n_days) + 0.25
                            
                            # Clip values to reasonable ranges
                            values = np.clip(values, 0, 1)
                            
                            results[index] = {
                                'dates': [d.strftime('%Y-%m-%d') for d in date_range],
                                'values': values.tolist()
                            }
                        
                        st.session_state.analysis_results = results
                        st.success("✅ Analysis completed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")

# MAIN CONTENT AREA
with col2:
    # Map Display
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin: 0 0 15px 0;">🗺️ Area Visualization</h3>', unsafe_allow_html=True)
    
    if st.session_state.selected_area:
        st.markdown(f"""
        <div style="background: #111111; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="color: #00ff88; margin: 0;">📍 {st.session_state.selected_area}</h4>
                    <p style="color: #999999; margin: 5px 0 0 0;">Selected for analysis</p>
                </div>
                <span class="status-badge">Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple map visualization using Plotly
        try:
            if PLOTLY_AVAILABLE:
                # Create a simple geographical visualization
                fig = go.Figure()
                
                # Add scatter for selected area (using dummy coordinates)
                if "United States" in st.session_state.selected_area:
                    lat, lon = 37.0902, -95.7129  # USA center
                elif "Canada" in st.session_state.selected_area:
                    lat, lon = 56.1304, -106.3468  # Canada center
                elif "United Kingdom" in st.session_state.selected_area:
                    lat, lon = 55.3781, -3.4360  # UK center
                elif "Australia" in st.session_state.selected_area:
                    lat, lon = -25.2744, 133.7751  # Australia center
                else:
                    lat, lon = 20, 0  # Default center
                
                fig.add_trace(go.Scattergeo(
                    lon=[lon],
                    lat=[lat],
                    mode='markers',
                    marker=dict(
                        size=20,
                        color='#00ff88',
                        symbol='circle'
                    ),
                    name='Selected Area',
                    hoverinfo='text',
                    text=[st.session_state.selected_area]
                ))
                
                fig.update_geos(
                    projection_type="natural earth",
                    showcountries=True,
                    countrycolor="white",
                    showcoastlines=True,
                    coastlinecolor="white",
                    showland=True,
                    landcolor="#111111",
                    showocean=True,
                    oceancolor="#0a0a0a",
                    showlakes=True,
                    lakecolor="#0a0a0a"
                )
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor='#0a0a0a',
                    plot_bgcolor='#0a0a0a',
                    geo=dict(
                        bgcolor='#0a0a0a',
                        lakecolor='#0a0a0a',
                        landcolor='#111111'
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⚠️ Map visualization requires Plotly. Please ensure it's installed.")
                
        except Exception as e:
            st.warning(f"Map display limited: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis Results Section
    if st.session_state.analysis_results and PLOTLY_AVAILABLE:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Results Header
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">')
        st.markdown('<h3 style="margin: 0;">📊 Analysis Results</h3>')
        st.markdown('<span class="status-badge">Complete</span>')
        st.markdown('</div>')
        
        results = st.session_state.analysis_results
        
        # Summary Statistics
        st.markdown('<h4>📈 Summary Statistics</h4>', unsafe_allow_html=True)
        
        summary_data = []
        for index, data in results.items():
            if data['values']:
                values = [v for v in data['values'] if v is not None]
                if values:
                    summary_data.append({
                        'Index': index,
                        'Mean': f"{sum(values) / len(values):.4f}",
                        'Min': f"{min(values):.4f}",
                        'Max': f"{max(values):.4f}",
                        'Data Points': len(values)
                    })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive Charts
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h4>📈 Vegetation Trends</h4>', unsafe_allow_html=True)
        
        # Create tabs for different indices
        index_tabs = st.tabs(list(results.keys()))
        
        for i, (index, data) in enumerate(results.items()):
            with index_tabs[i]:
                if data['dates'] and data['values']:
                    try:
                        # Create DataFrame
                        dates = [datetime.strptime(d, '%Y-%m-%d') for d in data['dates']]
                        df = pd.DataFrame({
                            'Date': dates,
                            'Value': data['values']
                        })
                        df = df.sort_values('Date')
                        
                        # Calculate moving average
                        if len(df) >= 7:
                            df['MA_7'] = df['Value'].rolling(window=7, min_periods=1).mean()
                        
                        # Create Plotly chart
                        fig = go.Figure()
                        
                        # Add main line
                        fig.add_trace(go.Scatter(
                            x=df['Date'],
                            y=df['Value'],
                            mode='lines',
                            name=f'{index}',
                            line=dict(color='#00ff88', width=2),
                            hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.4f}<extra></extra>'
                        ))
                        
                        # Add markers for significant points
                        fig.add_trace(go.Scatter(
                            x=[df['Date'].iloc[0], df['Date'].iloc[-1]],
                            y=[df['Value'].iloc[0], df['Value'].iloc[-1]],
                            mode='markers',
                            name='Start/End',
                            marker=dict(size=10, color='#ff4444'),
                            hoverinfo='skip'
                        ))
                        
                        # Add moving average if available
                        if 'MA_7' in df.columns:
                            fig.add_trace(go.Scatter(
                                x=df['Date'],
                                y=df['MA_7'],
                                mode='lines',
                                name='7-Day MA',
                                line=dict(color='#ffaa00', width=1, dash='dash'),
                                opacity=0.7
                            ))
                        
                        # Update layout
                        fig.update_layout(
                            title=f'{index} Vegetation Index Over Time',
                            plot_bgcolor='#0a0a0a',
                            paper_bgcolor='#0a0a0a',
                            font=dict(color='#ffffff'),
                            xaxis=dict(
                                gridcolor='#222222',
                                zerolinecolor='#222222',
                                title='Date',
                                tickformat='%b %Y'
                            ),
                            yaxis=dict(
                                gridcolor='#222222',
                                zerolinecolor='#222222',
                                title=f'{index} Value',
                                range=[max(0, df['Value'].min() - 0.1), min(1, df['Value'].max() + 0.1)]
                            ),
                            legend=dict(
                                bgcolor='rgba(0,0,0,0.5)',
                                bordercolor='#222222',
                                borderwidth=1
                            ),
                            hovermode='x unified',
                            height=400,
                            margin=dict(t=50, b=50, l=50, r=50)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show current value and trend
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                label="Current Value",
                                value=f"{df['Value'].iloc[-1]:.4f}",
                                delta=f"{(df['Value'].iloc[-1] - df['Value'].iloc[-2]):.4f}" if len(df) > 1 else None
                            )
                        with col2:
                            avg_value = df['Value'].mean()
                            st.metric(
                                label="Average",
                                value=f"{avg_value:.4f}"
                            )
                        with col3:
                            st.metric(
                                label="Data Points",
                                value=str(len(df))
                            )
                        
                    except Exception as e:
                        st.error(f"Error displaying {index}: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Export
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h4>💾 Export Data</h4>', unsafe_allow_html=True)
        
        # Create combined dataset for export
        export_data = []
        for index, data in results.items():
            for date, value in zip(data['dates'], data['values']):
                export_data.append({
                    'Date': date,
                    'Index': index,
                    'Value': value
                })
        
        export_df = pd.DataFrame(export_data)
        
        # Display preview
        st.dataframe(export_df.head(10), use_container_width=True)
        
        # Download button
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"khisba_gis_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="section-divider"></div>
<div style="text-align: center; color: #666666; font-size: 12px; padding: 20px 0;">
    <p style="margin: 5px 0;">🌿 <strong>KHISBA GIS</strong> • Interactive Vegetation Analytics Platform</p>
    <p style="margin: 5px 0;">Created with Streamlit • Plotly • Pandas</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
        <span class="status-badge">Streamlit Cloud</span>
        <span class="status-badge">Plotly Charts</span>
        <span class="status-badge">Interactive</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Display installation status
if not PLOTLY_AVAILABLE:
    st.error("""
    ❌ **CRITICAL: Plotly not installed!**
    
    The app requires Plotly for charts. Please ensure your `requirements.txt` includes:
    ```
    plotly>=5.17.0
    ```
    
    Current imports that failed: plotly.graph_objects, plotly.express
    """)
