import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk

# 设置页面配置
st.set_page_config(
    page_title="California Housing Data",
    page_icon="🏠",
    layout="wide"
)

# 应用标题
st.title("California Housing Data (1990)")

# 在侧边栏显示学生姓名
st.sidebar.title("About")
st.sidebar.write("**Developed by:** [JIaling Lu]")  # 请在这里替换为你的名字

# 加载数据
@st.cache_data
def load_data():
    try:
        # 尝试从本地文件加载
        df = pd.read_csv('housing.csv')
    except:
        try:
            # 如果本地文件不存在，尝试从网络加载示例数据
            url = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
            df = pd.read_csv(url)
        except:
            # 如果网络也失败，创建示例数据
            st.warning("使用示例数据，因为无法加载原始数据文件")
            np.random.seed(42)
            n_points = 1000
            df = pd.DataFrame({
                'longitude': np.random.uniform(-124.3, -114.3, n_points),
                'latitude': np.random.uniform(32.5, 42.0, n_points),
                'housing_median_age': np.random.randint(1, 52, n_points),
                'total_rooms': np.random.randint(2, 40000, n_points),
                'total_bedrooms': np.random.randint(1, 6500, n_points),
                'population': np.random.randint(3, 15000, n_points),
                'households': np.random.randint(1, 5000, n_points),
                'median_income': np.random.uniform(0.5, 15.0, n_points),
                'median_house_value': np.random.randint(15000, 500001, n_points),
                'ocean_proximity': np.random.choice(['INLAND', 'NEAR BAY', 'NEAR OCEAN', 'ISLAND'], n_points)
            })
    
    return df

df = load_data()

# 侧边栏过滤器
st.sidebar.title("Filters")

# 价格滑块
st.sidebar.subheader("Price Range Filter")
min_price = int(df['median_house_value'].min())
max_price = int(df['median_house_value'].max())
price_range = st.sidebar.slider(
    "Select price range:",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# 多选组件 - 位置类型
st.sidebar.subheader("Location Type")
location_options = df['ocean_proximity'].unique() if 'ocean_proximity' in df.columns else ['INLAND', 'NEAR BAY', 'NEAR OCEAN']
selected_locations = st.sidebar.multiselect(
    "Select location types:",
    options=location_options,
    default=location_options
)

# 单选按钮 - 收入水平
st.sidebar.subheader("Income Level")
income_level = st.sidebar.radio(
    "Select income level:",
    options=["All", "Low (≤2.5)", "Medium (>2.5 & <4.5)", "High (≥4.5)"]
)

# 根据过滤器筛选数据
filtered_df = df.copy()

# 价格筛选
filtered_df = filtered_df[
    (filtered_df['median_house_value'] >= price_range[0]) & 
    (filtered_df['median_house_value'] <= price_range[1])
]

# 位置类型筛选
if selected_locations:
    filtered_df = filtered_df[filtered_df['ocean_proximity'].isin(selected_locations)]

# 收入水平筛选
if income_level != "All":
    if income_level == "Low (≤2.5)":
        filtered_df = filtered_df[filtered_df['median_income'] <= 2.5]
    elif income_level == "Medium (>2.5 & <4.5)":
        filtered_df = filtered_df[(filtered_df['median_income'] > 2.5) & (filtered_df['median_income'] < 4.5)]
    elif income_level == "High (≥4.5)":
        filtered_df = filtered_df[filtered_df['median_income'] >= 4.5]

# 显示筛选结果信息
st.write(f"**Showing {len(filtered_df)} out of {len(df)} properties**")

# 地图显示
st.subheader("Housing Data Map")

if not filtered_df.empty:
    # 创建地图图层
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_df,
        get_position=['longitude', 'latitude'],
        get_color=[255, 0, 0, 160],
        get_radius=1000,
        pickable=True
    )
    
    # 设置视图
    view_state = pdk.ViewState(
        latitude=filtered_df['latitude'].mean(),
        longitude=filtered_df['longitude'].mean(),
        zoom=5,
        pitch=0
    )
    
    # 创建地图
    map_chart = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            'html': '<b>Median Value:</b> ${median_house_value}<br/>'
                   '<b>Income:</b> {median_income}<br/>'
                   '<b>Location:</b> {ocean_proximity}',
            'style': {
                'color': 'white'
            }
        }
    )
    
    st.pydeck_chart(map_chart)
else:
    st.warning("No data available for the selected filters.")

# 直方图
st.subheader("Distribution of Median House Values")

if not filtered_df.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(filtered_df['median_house_value'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Median House Value ($)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of House Values')
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
else:
    st.warning("No data available for histogram.")

# 数据显示
st.subheader("Filtered Data")
st.dataframe(filtered_df.head(100))  # 只显示前100行

# 统计信息
st.sidebar.title("Data Summary")
st.sidebar.write(f"Total properties: {len(df)}")
st.sidebar.write(f"Filtered properties: {len(filtered_df)}")
st.sidebar.write(f"Average price: ${filtered_df['median_house_value'].mean():,.0f}")
st.sidebar.write(f"Average income: {filtered_df['median_income'].mean():.2f}")

st.sidebar.info("See more filters above ↑")