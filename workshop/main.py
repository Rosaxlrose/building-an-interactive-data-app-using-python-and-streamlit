import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go

def load_data():
    try:
        df = pd.read_csv('../datasets/1642645053.csv', encoding="tis-620")
        
        # Clean column names and strip whitespace
        df.columns = df.columns.str.strip()
        
        # Explicitly convert numeric columns to appropriate types
        numeric_columns = [
            'จำนวนรวม โคเนื้อ ทั้งสิ้น (ตัว)',
            'จำนวนรวม โคนม ทั้งสิ้น (ตัว)', 
            'จำนวนรวม กระบือ ทั้งสิ้น (ตัว)',
            'จำนวนรวม สุกร ทั้งสิ้น (ตัว)',
            'จำนวนรวม ไก่ ทั้งสิ้น (ตัว)',
            'จำนวนรวม เป็ด ทั้งสิ้น (ตัว)',
            'จำนวนรวม แพะ ทั้งสิ้น (ตัว)',
            'จำนวนรวม แกะ ทั้งสิ้น (ตัว)'
        ]
        
        # Convert to numeric, replacing any non-numeric values with NaN
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

        def convert_thai_number(value):
            try:
                # Remove commas and convert to float
                return float(str(value).replace(',', ''))
            except (ValueError, TypeError):
                return pd.NA
        
        # Convert numeric columns
        for col in numeric_columns:
            df[col] = df[col].apply(convert_thai_number)
        
        # Find and convert farmer columns
        farmer_columns = [
            col for col in df.columns 
            if 'เกษตรกร' in col and 'ราย' in col
        ]
        
        for col in farmer_columns:
            df[col] = df[col].apply(convert_thai_number)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.set_page_config(page_title="Thailand Livestock Analysis", layout="wide")
    
    # Title and introduction
    st.title("🐄 Thailand Livestock Data Analysis")
    st.markdown("""
    ## Comprehensive Livestock Statistics Dashboard
    
    This dashboard provides an in-depth analysis of livestock data across different regions in Thailand.
    """)
    
    # Load data
    df = load_data()
    
    if df is None:
        return
    
    # Sidebar for filters and options
    st.sidebar.header("🔍 Visualization Controls")
    
    # Analysis Options
    analysis_type = st.sidebar.selectbox("Select Analysis Type", [
        "Overview of Livestock Types",
        "Regional Livestock Distribution",
        "Comparative Livestock Analysis",
        "Farmers and Livestock Correlation"
    ])
    
    # Main Analysis Section
    if analysis_type == "Overview of Livestock Types":
        st.header("Overview of Livestock Types")
        
        # Aggregate livestock types
        livestock_columns = [
            'จำนวนรวม โคเนื้อ ทั้งสิ้น (ตัว)',
            'จำนวนรวม โคนม ทั้งสิ้น (ตัว)', 
            'จำนวนรวม กระบือ ทั้งสิ้น (ตัว)',
            'จำนวนรวม สุกร ทั้งสิ้น (ตัว)',
            'จำนวนรวม ไก่ ทั้งสิ้น (ตัว)',
            'จำนวนรวม เป็ด ทั้งสิ้น (ตัว)',
            'จำนวนรวม แพะ ทั้งสิ้น (ตัว)',
            'จำนวนรวม แกะ ทั้งสิ้น (ตัว)'
        ]
        
        total_livestock = df[livestock_columns].sum()
        
        # Create pie chart
        fig = px.pie(
            values=total_livestock.values, 
            names=total_livestock.index, 
            title='Total Livestock Distribution in Thailand'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed breakdown
        st.subheader("Detailed Livestock Breakdown")
        st.dataframe(total_livestock.reset_index())
    
    elif analysis_type == "Regional Livestock Distribution":
        st.header("Regional Livestock Distribution")
        
        # Select column for regional analysis
        region_column = st.selectbox("Select Livestock Type", [
            'โคเนื้อ', 'โคนม', 'กระบือ', 'สุกร', 'ไก่', 'เป็ด', 'แพะ', 'แกะ'
        ])
        
        # Columns to aggregate
        total_columns = [
            col for col in df.columns if region_column in col and 'รวม' in col and 'ตัว' in col
        ]
        
        if total_columns:
            # Group by province and sum
            provincial_data = df.groupby('สถานที่เลี้ยงสัตว์ จังหวัด')[total_columns[0]].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=provincial_data.index, 
                y=provincial_data.values, 
                title=f'Provincial Distribution of {region_column}'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top 10 provinces
            st.subheader(f"Top 10 Provinces for {region_column}")
            st.dataframe(provincial_data.head(10))
    
    elif analysis_type == "Comparative Livestock Analysis":
        st.header("Comparative Livestock Analysis")
        
        # Select columns for comparison
        col1, col2 = st.columns(2)
        
        with col1:
            livestock_type1 = st.selectbox("First Livestock Type", [
                'โคเนื้อ', 'โคนม', 'กระบือ', 'สุกร', 'ไก่', 'เป็ด', 'แพะ', 'แกะ'
            ], key='type1')
        
        with col2:
            livestock_type2 = st.selectbox("Second Livestock Type", [
                'โคนม', 'โคเนื้อ', 'กระบือ', 'สุกร', 'ไก่', 'เป็ด', 'แพะ', 'แกะ'
            ], key='type2')
        
        
        def get_total_column(livestock_type):
            columns = [
                col for col in df.columns 
                if livestock_type in col and 'รวม' in col and 'ตัว' in col
            ]
            return columns[0] if columns else None
        
        column1 = get_total_column(livestock_type1)
        column2 = get_total_column(livestock_type2)
        
        
        if column1 and column2:
            # Scatter plot comparing two livestock types
            fig = px.scatter(
                df, 
                x=column1, 
                y=column2, 
                hover_data=['สถานที่เลี้ยงสัตว์ จังหวัด'],
                title=f'Comparison between {livestock_type1} and {livestock_type2}'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Farmers and Livestock Correlation":
        st.header("Farmers and Livestock Correlation")
        
        # Select livestock type
        livestock_type = st.selectbox("Select Livestock Type", [
            'โคเนื้อ', 'โคนม', 'กระบือ', 'สุกร', 'ไก่', 'เป็ด', 'แพะ', 'แกะ'
        ])
        
        # Find total and farmer columns
        total_column = [
            col for col in df.columns 
            if livestock_type in col and 'รวม' in col and 'ตัว' in col
        ][0]
        
        farmer_column = [
            col for col in df.columns 
            if livestock_type in col and 'เกษตรกร' in col and 'ราย' in col
        ][0]
        
        # Scatter plot of farmers vs total livestock
        fig = px.scatter(
            df, 
            x=farmer_column, 
            y=total_column, 
            hover_data=['สถานที่เลี้ยงสัตว์ จังหวัด'],
            title=f'Correlation between Farmers and {livestock_type} Population'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    # Footer
    st.markdown("---")
    st.markdown("🌾 Data Analysis of Thai Livestock Statistics")

if __name__ == "__main__":
    main()