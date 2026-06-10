from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.features.build_features import add_lag_features, add_rolling_features, add_time_features
from src.review_store import backend_label, healthcheck, load_reviews, log_predictions, review_summary, save_review
from src.settings import get_settings

st.set_page_config(page_title='Device Storage Growth Forecaster', page_icon='📦', layout='wide')
sns.set_theme(style='whitegrid')

SETTINGS = get_settings()
DATA_PATH = ROOT / 'data' / 'synthetic' / 'synthetic_storage_usage.csv'
REPORTS_DIR = ROOT / 'reports'
MODELS_DIR = ROOT / 'models'
HORIZONS = [30, 60, 90]
REQUIRED_UPLOAD_COLUMNS = [
    'user_id', 'profile', 'date', 'day_index', 'total_capacity_gb', 'used_gb', 'free_gb', 'used_pct',
    'photos_gb', 'videos_gb', 'apps_gb', 'documents_gb', 'system_gb', 'other_gb', 'daily_delta_gb', 'cleanup_event'
]
MODEL_LABELS = {
    'baseline_v2_ridge': 'Baseline V2 (Ridge)',
    'prophet_per_user': 'Prophet',
    'xgboost_direct': 'XGBoost',
}


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, parse_dates=['date']).sort_values(['user_id', 'date'])


@st.cache_data
def load_metrics() -> pd.DataFrame:
    files = {
        'baseline_v2_ridge': REPORTS_DIR / 'baseline_v2_metrics.csv',
        'prophet_per_user': REPORTS_DIR / 'prophet_metrics.csv',
        'xgboost_direct': REPORTS_DIR / 'xgboost_metrics.csv',
    }
    frames = []
    for model_name, path in files.items():
        if path.exists():
            frame = pd.read_csv(path)
            frame['model'] = frame.get('model', model_name)
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=['model', 'horizon_days', 'mae', 'rmse', 'mape'])


@st.cache_resource
def load_xgboost_models():
    models = {}
    for horizon in HORIZONS:
        path = MODELS_DIR / f'xgboost_h{horizon}.joblib'
        if path.exists():
            models[horizon] = joblib.load(path)
    return models



def make_user_hash(seed: str) -> str:
    return hashlib.sha256(seed.encode('utf-8')).hexdigest()[:24]



def prepare_latest_feature_row(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work['date'] = pd.to_datetime(work['date'])
    work = work.sort_values(['user_id', 'date']).copy()
    work = add_time_features(work)
    work = add_lag_features(work, lags=(1, 7, 14, 30))
    work = add_rolling_features(work, windows=(7, 30))
    return work.groupby('user_id').tail(1).copy()



def format_model_name(name: str) -> str:
    return MODEL_LABELS.get(name, name)



def metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div style='padding:1rem;border-radius:1rem;background:#f5f7fb;border:1px solid #e5e7eb;'>
            <div style='font-size:0.9rem;color:#6b7280;'>{label}</div>
            <div style='font-size:1.6rem;font-weight:700;color:#111827;'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title('📦 Device Storage Growth Forecaster')
st.caption('Forecast device storage growth, compare models, and capture production-style user feedback.')

if not DATA_PATH.exists():
    st.error('Synthetic dataset not found. Run the data-generation pipeline first.')
    st.stop()

df = load_data()
metrics_df = load_metrics()
models = load_xgboost_models()
store_health = healthcheck()
summary = review_summary() if store_health.get('ok') else {'total_reviews': 0, 'avg_rating': None, 'total_predictions_logged': 0, 'backend': backend_label()}

with st.sidebar:
    st.header('Control Center')
    profiles = ['All'] + sorted(df['profile'].unique().tolist())
    selected_profile = st.selectbox('Profile filter', profiles)
    profile_df = df if selected_profile == 'All' else df[df['profile'] == selected_profile]
    available_users = sorted(profile_df['user_id'].unique().tolist())
    selected_user = st.selectbox('Sample user', available_users)
    st.markdown('---')
    st.write('**Deployment status**')
    st.write(f"- Review store: {'✅' if store_health.get('ok') else '⚠️'} {summary['backend']}")
    st.write(f"- App environment: `{SETTINGS.environment}`")
    st.write(f"- XGBoost models: {'✅ ready' if len(models) == 3 else '⚠️ partial'}")
    st.write(f"- Reviews saved: {summary['total_reviews']}")
    st.write(f"- Predictions logged: {summary['total_predictions_logged']}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card('Rows', f"{len(df):,}")
with col2:
    metric_card('Users', str(df['user_id'].nunique()))
with col3:
    metric_card('Profiles', str(df['profile'].nunique()))
with col4:
    best_mae = metrics_df.loc[metrics_df['mae'].idxmin(), 'mae'] if not metrics_df.empty else None
    metric_card('Best MAE', f"{best_mae:.2f}" if best_mae is not None else 'N/A')

overview_tab, data_builder_tab, forecast_tab, benchmark_tab, reviews_tab = st.tabs(['Overview', 'Data Builder', 'Forecast Lab', 'Model Benchmarks', 'Reviews & Deploy'])

with overview_tab:
    st.subheader('Behavior Explorer')
    user_df = df[df['user_id'] == selected_user].sort_values('date')
    c1, c2 = st.columns([2, 1])
    with c1:
        fig, ax = plt.subplots(figsize=(11, 4.5))
        ax.plot(user_df['date'], user_df['used_gb'], label='Used GB', linewidth=2)
        ax.plot(user_df['date'], user_df['total_capacity_gb'], label='Capacity', linestyle='--', alpha=0.8)
        ax.set_title(f'User trajectory — {selected_user} ({user_df["profile"].iloc[0]})')
        ax.set_ylabel('GB')
        ax.grid(alpha=0.3)
        ax.legend()
        st.pyplot(fig)
    with c2:
        latest = user_df.iloc[-1]
        st.metric('Current used GB', f"{latest['used_gb']:.2f}")
        st.metric('Current free GB', f"{latest['free_gb']:.2f}")
        st.metric('Current used %', f"{latest['used_pct']:.2f}%")
        st.metric('Cleanup events', int(user_df['cleanup_event'].sum()))

    st.markdown('### Storage composition for selected user')
    comp_cols = ['system_gb', 'apps_gb', 'photos_gb', 'videos_gb', 'documents_gb', 'other_gb']
    fig2, ax2 = plt.subplots(figsize=(11, 4.5))
    ax2.stackplot(user_df['date'], [user_df[c] for c in comp_cols], labels=[c.replace('_gb', '').title() for c in comp_cols], alpha=0.9)
    ax2.legend(loc='upper left', ncol=3, fontsize=8)
    ax2.set_ylabel('GB')
    ax2.set_title('Storage composition over time')
    st.pyplot(fig2)

    with st.expander('Preview filtered data'):
        st.dataframe(profile_df.head(100), use_container_width=True)

with data_builder_tab:
    st.subheader('📋 CSV Data Builder')
    st.write('**Easy way to create your storage data CSV!** No confusing formats - just fill in simple information and download.')
    
    builder_mode = st.radio('Choose a method:', ['📊 See Example Data', '🔨 Generate Template', '📥 Download Real Example'])
    
    if builder_mode == '📊 See Example Data':
        st.write('### Here\'s what your data should look like:')
        example_df = pd.read_csv(ROOT / 'data' / 'storage_data_template.csv')
        st.info('✓ This is a real example with 31 days of storage data from one device')
        st.dataframe(example_df.head(15), use_container_width=True)
        st.write(f'**Total rows in example:** {len(example_df)} (31 days)')
        
        st.markdown('### Column meanings:')
        col_info = {
            'user_id': 'Your device ID (e.g., "my_phone_001")',
            'profile': 'Device type (e.g., "heavy_user", "light_user")',
            'date': 'The date (YYYY-MM-DD format)',
            'day_index': 'Days since start (0, 1, 2, ...)',
            'total_capacity_gb': 'Total storage size (e.g., 512GB)',
            'used_gb': 'How much you\'re using',
            'free_gb': 'How much is free (capacity - used)',
            'used_pct': 'Used percentage (0-100)',
            'photos_gb': 'Storage used by photos',
            'videos_gb': 'Storage used by videos',
            'apps_gb': 'Storage used by apps',
            'documents_gb': 'Storage used by documents',
            'system_gb': 'Storage used by system',
            'other_gb': 'Storage used by other files',
            'daily_delta_gb': 'How much changed today',
            'cleanup_event': 'Did you delete stuff? (0=no, 1=yes)',
        }
        
        cols_display = st.columns(2)
        for i, (col, desc) in enumerate(col_info.items()):
            with cols_display[i % 2]:
                st.write(f"**{col}**  \n{desc}")
    
    elif builder_mode == '🔨 Generate Template':
        st.write('### Quick template generator')
        st.write('Tell us about your device, and we\'ll create a blank template you can fill in:')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            device_id = st.text_input('Device ID', value='my_device_001', help='Your phone/tablet ID')
            days_of_data = st.number_input('Days of data you have', min_value=7, max_value=365, value=30, help='How many days of data?')
        with col2:
            profile = st.text_input('Device profile', value='heavy_user', help='e.g. heavy_user, light_user, media_heavy')
            capacity = st.number_input('Storage capacity (GB)', min_value=32, max_value=2048, value=256, help='Total storage size')
        with col3:
            start_date = st.date_input('Start date', value=pd.Timestamp.now() - pd.Timedelta(days=29))
        
        if st.button('📥 Generate blank template', key='gen_template'):
            # Create blank template
            dates = pd.date_range(start=start_date, periods=int(days_of_data), freq='D')
            template_data = {
                'user_id': [device_id] * len(dates),
                'profile': [profile] * len(dates),
                'date': dates.strftime('%Y-%m-%d'),
                'day_index': range(len(dates)),
                'total_capacity_gb': [float(capacity)] * len(dates),
                'used_gb': [0.0] * len(dates),
                'free_gb': [float(capacity)] * len(dates),
                'used_pct': [0.0] * len(dates),
                'photos_gb': [0.0] * len(dates),
                'videos_gb': [0.0] * len(dates),
                'apps_gb': [0.0] * len(dates),
                'documents_gb': [0.0] * len(dates),
                'system_gb': [0.0] * len(dates),
                'other_gb': [0.0] * len(dates),
                'daily_delta_gb': [0.0] * len(dates),
                'cleanup_event': [0] * len(dates),
            }
            template_df = pd.DataFrame(template_data)
            template_csv = template_df.to_csv(index=False)
            
            st.success(f'✅ Template created with {len(template_df)} rows')
            st.dataframe(template_df.head(10), use_container_width=True)
            
            st.download_button(
                label=f'📥 Download template ({len(template_df)} rows)',
                data=template_csv,
                file_name=f'storage_data_{device_id}_{start_date.strftime("%Y%m%d")}.csv',
                mime='text/csv',
                key='download_gen_template'
            )
            
            st.info("""
            **Next steps:**
            1. Download the CSV above ⬆️
            2. Open it in Excel or Google Sheets
            3. Fill in your actual storage numbers
            4. Come back and upload it in the **Forecast Lab** tab
            """)
    
    else:  # Download Real Example
        st.write('### Download the example data')
        st.write('This is real data from one device over 31 days. You can use it to test the forecaster:')
        
        example_df = pd.read_csv(ROOT / 'data' / 'storage_data_template.csv')
        example_csv = example_df.to_csv(index=False)
        
        col_down1, col_down2 = st.columns([2, 1])
        with col_down1:
            st.dataframe(example_df.head(10), use_container_width=True)
        with col_down2:
            st.metric('Rows', len(example_df))
            st.metric('Days', len(example_df))
            st.metric('Device ID', 'device_001')
        
        st.download_button(
            label='📥 Download example CSV',
            data=example_csv,
            file_name='storage_data_example.csv',
            mime='text/csv',
            key='download_example_csv'
        )

with forecast_tab:
    st.subheader('XGBoost Inference Lab')
    st.write('Run the production-candidate XGBoost model on a sample user or your own CSV. Every forecast can be logged for later product analysis.')
    
    # Quick help
    st.info('� **Need a CSV?** Go to the **Data Builder** tab to see examples, generate a template, or download sample data!')
    
    source = st.radio('Forecast source', ['Sample user from dataset', 'Upload CSV'], horizontal=True)
    input_df = None
    source_name = 'sample_user'
    user_hash = make_user_hash(selected_user)

    if source == 'Sample user from dataset':
        input_df = df[df['user_id'] == selected_user].copy()
        st.info(f'Using sample user {selected_user} with {len(input_df)} historical rows.')
    else:
        source_name = 'uploaded_csv'
        uploaded = st.file_uploader('Upload a CSV with the project schema', type=['csv'])
        if uploaded is not None:
            try:
                uploaded_df = pd.read_csv(uploaded)
            except Exception as e:
                st.error(f'❌ Failed to read CSV: {str(e)}')
                uploaded_df = None
            
            if uploaded_df is not None:
                # Validate columns
                missing_cols = [c for c in REQUIRED_UPLOAD_COLUMNS if c not in uploaded_df.columns]
                if missing_cols:
                    st.error(f'❌ Missing required columns: {", ".join(missing_cols)}')
                    st.info(f'✓ Expected 16 columns: {", ".join(REQUIRED_UPLOAD_COLUMNS)}')
                    st.info(f'✓ Your CSV has {len(uploaded_df.columns)} columns: {", ".join(uploaded_df.columns)}')
                else:
                    # Additional validation checks
                    validation_errors = []
                    validation_warnings = []
                    
                    # Check row count
                    if len(uploaded_df) < 7:
                        validation_errors.append(f'Need at least 7 days of data; you have {len(uploaded_df)} rows')
                    elif len(uploaded_df) < 30:
                        validation_warnings.append(f'Only {len(uploaded_df)} rows provided; 30+ rows recommended for better forecasts')
                    
                    # Parse date column
                    try:
                        uploaded_df['date'] = pd.to_datetime(uploaded_df['date'])
                    except Exception as e:
                        validation_errors.append(f'Date format error: {str(e)}. Use YYYY-MM-DD format.')
                    
                    # Check numeric columns
                    numeric_cols = ['total_capacity_gb', 'used_gb', 'free_gb', 'used_pct', 'photos_gb', 
                                   'videos_gb', 'apps_gb', 'documents_gb', 'system_gb', 'other_gb', 
                                   'daily_delta_gb']
                    for col in numeric_cols:
                        if col in uploaded_df.columns:
                            try:
                                uploaded_df[col] = pd.to_numeric(uploaded_df[col])
                                # Check for negative values
                                if (uploaded_df[col] < 0).any():
                                    validation_errors.append(f'Column "{col}" has negative values. All GB values must be ≥ 0.')
                            except ValueError:
                                validation_errors.append(f'Column "{col}" contains non-numeric values.')
                    
                    # Check capacity vs used
                    if 'total_capacity_gb' in uploaded_df.columns and 'used_gb' in uploaded_df.columns:
                        violations = (uploaded_df['used_gb'] > uploaded_df['total_capacity_gb']).sum()
                        if violations > 0:
                            validation_errors.append(f'Found {violations} rows where used_gb > total_capacity_gb. Check your data.')
                    
                    # Check cleanup_event is binary
                    if 'cleanup_event' in uploaded_df.columns:
                        invalid_cleanup = ~uploaded_df['cleanup_event'].isin([0, 1])
                        if invalid_cleanup.any():
                            validation_warnings.append(f'cleanup_event should be 0 or 1; found other values in {invalid_cleanup.sum()} rows')
                    
                    # Show results
                    if validation_errors:
                        for error in validation_errors:
                            st.error(f'❌ {error}')
                    else:
                        if validation_warnings:
                            for warning in validation_warnings:
                                st.warning(f'⚠️ {warning}')
                        
                        input_df = uploaded_df.copy()
                        first_user = str(input_df['user_id'].iloc[0]) if 'user_id' in input_df.columns else 'uploaded'
                        user_hash = make_user_hash(first_user)
                        
                        st.success(f'✅ CSV validated successfully! {len(input_df):,} rows loaded.')
                        
                        # Show data summary
                        col_summary1, col_summary2, col_summary3 = st.columns(3)
                        with col_summary1:
                            st.metric('Total rows', f'{len(input_df):,}')
                        with col_summary2:
                            unique_users = input_df['user_id'].nunique()
                            st.metric('Unique users', unique_users)
                        with col_summary3:
                            date_range = (input_df['date'].max() - input_df['date'].min()).days + 1
                            st.metric('Date range (days)', date_range)
                        
                        # Show data preview and stats
                        with st.expander('📊 Data preview & statistics', expanded=True):
                            tab_preview, tab_stats = st.tabs(['Preview', 'Statistics'])
                            
                            with tab_preview:
                                st.dataframe(input_df.head(20), use_container_width=True)
                            
                            with tab_stats:
                                st.write('**Key statistics:**')
                                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                                with col_stat1:
                                    avg_used = input_df['used_gb'].mean()
                                    st.metric('Avg used GB', f'{avg_used:.2f}')
                                with col_stat2:
                                    max_used = input_df['used_gb'].max()
                                    st.metric('Max used GB', f'{max_used:.2f}')
                                with col_stat3:
                                    cleanups = input_df['cleanup_event'].sum()
                                    st.metric('Total cleanups', int(cleanups))
                                with col_stat4:
                                    avg_capacity = input_df['total_capacity_gb'].mean()
                                    st.metric('Avg capacity GB', f'{avg_capacity:.2f}')
                                
                                st.write('**Column ranges:**')
                                stats_table = pd.DataFrame({
                                    'Column': numeric_cols,
                                    'Min': [input_df[col].min() if col in input_df.columns else 'N/A' for col in numeric_cols],
                                    'Max': [input_df[col].max() if col in input_df.columns else 'N/A' for col in numeric_cols],
                                    'Mean': [input_df[col].mean() if col in input_df.columns else 'N/A' for col in numeric_cols],
                                })
                                st.dataframe(stats_table, use_container_width=True)

    if input_df is not None:
        latest_feature_row = prepare_latest_feature_row(input_df)
        if latest_feature_row.empty:
            st.warning('Not enough rows to compute features.')
        elif len(models) != 3:
            st.error('XGBoost model files are missing. Run scripts/train_xgboost.py first.')
        else:
            latest_feature_row = latest_feature_row.tail(1)
            forecast_rows = []
            capacity = float(latest_feature_row['total_capacity_gb'].iloc[0])
            for horizon in HORIZONS:
                pred = float(models[horizon].predict(latest_feature_row)[0])
                pred = max(0.0, min(pred, capacity * 0.985))
                forecast_rows.append({
                    'horizon_days': horizon,
                    'predicted_used_gb': round(pred, 3),
                    'predicted_used_pct': round(100.0 * pred / capacity, 2),
                    'capacity_gb': round(capacity, 3),
                })
            forecast_df = pd.DataFrame(forecast_rows)
            st.markdown('### Forecast output')
            st.dataframe(forecast_df, use_container_width=True)

            col_a, col_b = st.columns([2, 1])
            with col_a:
                fig3, ax3 = plt.subplots(figsize=(8, 4))
                ax3.plot(forecast_df['horizon_days'], forecast_df['predicted_used_gb'], marker='o', linewidth=2)
                ax3.set_xticks(HORIZONS)
                ax3.set_xlabel('Forecast horizon (days)')
                ax3.set_ylabel('Predicted used GB')
                ax3.set_title('XGBoost direct forecasts')
                ax3.grid(alpha=0.3)
                st.pyplot(fig3)
            with col_b:
                risk_horizon = forecast_df[forecast_df['predicted_used_pct'] >= 85]
                if risk_horizon.empty:
                    st.success('No critical storage risk detected in the 90-day window.')
                else:
                    first_risk = int(risk_horizon['horizon_days'].iloc[0])
                    st.warning(f'Predicted storage pressure crosses 85% by day {first_risk}.')

            if st.button('Log this forecast event', key='log_forecast_event'):
                log_predictions('XGBoost', source_name, forecast_rows, user_hash=user_hash)
                st.success('Forecast event logged to the review store backend.')

with benchmark_tab:
    st.subheader('Model Benchmark Center')
    if metrics_df.empty:
        st.warning('Metrics files not found.')
    else:
        pretty = metrics_df.copy()
        pretty['model'] = pretty['model'].map(format_model_name)
        st.dataframe(pretty.sort_values(['horizon_days', 'mae']), use_container_width=True)
        metric_choice = st.selectbox('Metric to compare', ['mae', 'rmse', 'mape'])
        fig4, ax4 = plt.subplots(figsize=(10, 4.8))
        sns.barplot(data=pretty, x='horizon_days', y=metric_choice, hue='model', ax=ax4)
        ax4.set_title(f'{metric_choice.upper()} by model and horizon')
        ax4.set_xlabel('Forecast horizon (days)')
        ax4.set_ylabel(metric_choice.upper())
        st.pyplot(fig4)
        best = pretty.loc[pretty.groupby('horizon_days')[metric_choice].idxmin(), ['horizon_days', 'model', metric_choice]]
        st.markdown('### Best model by selected metric')
        st.dataframe(best, use_container_width=True)

with reviews_tab:
    st.subheader('Managed Reviews + Production Readiness')
    st.write('This app can now use a managed PostgreSQL database through `DATABASE_URL`. Local SQLite remains as a fallback for development only.')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Review backend', summary['backend'])
    with c2:
        st.metric('Total reviews', summary['total_reviews'])
    with c3:
        st.metric('Average rating', f"{summary['avg_rating']:.2f}" if summary.get('avg_rating') is not None else 'N/A')

    with st.form('review_form', clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input('Name')
            role = st.text_input('Role / team')
        with col_b:
            rating = st.slider('Rating', 1, 5, 5)
            model_used = st.selectbox('Model used', ['XGBoost', 'Prophet', 'Baseline V2'])
        comment = st.text_area('Review / feedback')
        submit_review = st.form_submit_button('Save review')
        if submit_review:
            if not comment.strip():
                st.warning('Please add a short review before submitting.')
            else:
                save_review(name=name, role=role, rating=rating, model_used=model_used, comment=comment, user_hash=make_user_hash((name or 'anon') + model_used))
                st.success('Review saved successfully.')
                st.cache_data.clear()

    rows = load_reviews(limit=200) if store_health.get('ok') else []
    if rows:
        review_df = pd.DataFrame(rows)
        
        # Export section
        st.markdown('### Export & Analytics')
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            if st.button('📥 Export reviews to CSV', key='export_reviews'):
                all_reviews = load_reviews(limit=50000)
                if all_reviews:
                    export_df = pd.DataFrame(all_reviews)
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="Download reviews.csv",
                        data=csv,
                        file_name=f"reviews_{pd.Timestamp.now().date()}.csv",
                        mime="text/csv",
                        key="download_reviews_csv"
                    )
        
        with col_exp2:
            # Summary statistics
            st.metric('Reviews this session', len(review_df))
        
        st.markdown('### Recent reviews')
        st.dataframe(review_df, use_container_width=True)
    else:
        st.info('No reviews yet. Submit the first one from this app.')

    st.markdown('### Production checklist')
    st.markdown('- managed PostgreSQL via `DATABASE_URL`\n- model artifacts versioned in `models/`\n- forecast event logging\n- input validation for uploads\n- Docker image + healthcheck\n- secret-driven configuration with `.env` or Streamlit secrets')
