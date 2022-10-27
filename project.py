import json
import time
import random
import datetime
import pytz

import requests
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components  # 可用于定义图表长宽
from streamlit_echarts import st_echarts  # 组件，渲染图表与pyecharts结合

import graphviz  # 绘制向图
import altair as alt
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
from pyecharts.charts import *
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

from PIL import Image
from io import BytesIO
import emoji

Temp_emo = emoji.emojize('Temperature' + ':sunflower:')
BodyTemp_emo = emoji.emojize('Body Temperature' + ':maple_leaf:')
Humidity_emo = emoji.emojize('Humidity' + ':droplet:')
Weather_emo = emoji.emojize('Weather' + ':balloon:')
Weather_day_emo = emoji.emojize('WeatherDay' + '":balloon::sun:')
Weather_night__emo = emoji.emojize('WeatherNight' + ':balloon::milky_way:')
Wind_emo = emoji.emojize('Wind' + ':wind_chime:')
Wind_day_emo = emoji.emojize('WindDay' + ':wind_chime::sun:')
Wind_night_emo = emoji.emojize('WindNight' + ':wind_chime::milky_way:')

# beijing = pytz.timezone('Asia/Beijing')
def main():
    st.set_page_config(page_title="粉色Mojito", page_icon=":rainbow:", layout="wide", initial_sidebar_state="auto")
    st.title('粉色Mojito:sparkling_heart:')
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    charts_mapping = {
        'Line': 'line_chart', 'Bar': 'bar_chart', 'Area': 'area_chart', 'Hist': 'pyplot', 'Altair': 'altair_chart',
        'Map': 'map', 'Graphviz': 'graphviz_chart', 'Pyechart': ''
    }

    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    else:
        st.session_state.first_visit = False

    if st.session_state.first_visit:
        st.session_state.date_time = datetime.datetime.now()  # + datetime.timedelta(hours=8)
        # st.session_state.random_chart_index = random.choice(range(len(charts_mapping)))
        # st.session_state.my_random = MyRandom(random.randint(1, 1000000))
        st.session_state.city_mapping, st.session_state.random_city_index = get_city_mapping()
        st.balloons()
        st.snow()

    music = st.sidebar.radio(emoji.emojize('Select Music You Like :musical_note:'), ['Mojito', '粉色海洋'],
                             index=random.choice(range(2)))
    st.sidebar.write(emoji.emojize(f'正在播放 {music}-周杰伦 :musical_score:'))
    audio_bytes = get_audio_bytes(music)
    st.sidebar.audio(audio_bytes, format='audio/mp3')

    d = st.sidebar.date_input('Date 📆', st.session_state.date_time.date())
    t = st.sidebar.time_input('Time⏳', st.session_state.date_time.time())
    t = f'{t}'.split('.')[0]  # datetime.date_time.time()最后面会显示'.xxx'
    nighttime = ['00', '01', '02', '03', '04', '05', '18', '19', '20', '21', '22', '23']  # 后面判断是否为晚上
    st.sidebar.write(f'Current time is {d} {t}')
    city = st.sidebar.selectbox(emoji.emojize('Select a city you like(按首字母顺序):rainbow:'),
                                st.session_state.city_mapping.keys(),
                                index=st.session_state.random_city_index)
    chart = st.sidebar.selectbox(emoji.emojize('Select a chart You Like :bar_chart:'), charts_mapping.keys(),
                                 index=1)
    color = st.sidebar.color_picker('Pick A Color', '#00f900')
    st.sidebar.write('The current color is', color)
    with st.container():
        if t[:2] in nighttime:
            st.markdown(f'### {city}天气预报:star::moon:')
        else:
            st.markdown(f'### {city}天气预报:sunrise::palm_tree:')
        st.markdown(' 数据来源[墨迹天气](<https://html5.moji.com/tpd/mojiweather_pc/index.html>)')
        forecastToday, df_forecastHours, df_forecastDays = get_city_weather(st.session_state.city_mapping[city])
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric('Weather', forecastToday['weather'])
        col2.metric('Temperature', forecastToday['temp'])
        col3.metric('Body Temperature', forecastToday['realFeel'])
        col4.metric('Humidity', forecastToday['humidity'])
        col5.metric('Wind', forecastToday['wind'])
        col6.metric('UpdateTime', forecastToday['updateTime'])

        option = (
        'LIGHT', 'CHALK', 'DARK', 'ESSOS', 'INFOGRAPHIC', 'MACARONS', 'PURPLE_PASSION', 'ROMA', 'ROMANTIC', 'SHINE',
        'VINTAGE', 'WALDEN', 'WESTEROS', 'WONDERLAND')
        options = st.selectbox("Select a theme for the chart below.", option)


        c1 = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.DARK if t[:2] in nighttime else ThemeType.LIGHT))
                .add_xaxis(df_forecastHours.index.to_list())  # 添加x,y轴
                .add_yaxis('Temperature', df_forecastHours[Temp_emo].values.tolist())
                .add_yaxis('Body Temperature', df_forecastHours[BodyTemp_emo].values.tolist())
                .set_global_opts(
                title_opts=opts.TitleOpts(title="24 Hours Forecast"),  # 标题
                xaxis_opts=opts.AxisOpts(type_="category"),  # 坐标轴类型,'category'适用于离散的数据
                yaxis_opts=opts.AxisOpts(type_="value", axislabel_opts=opts.LabelOpts(formatter="{value} °C")),  # 连续数据
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")  # 坐标轴触发提示框，’十字‘瞄准线
            )
                .set_series_opts(label_opts=opts.LabelOpts(formatter=JsCode("function(x){return x.data[1] + '°C';}")))
            # ?
        )
        c2 = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.CHALK if t[:2] in nighttime else ThemeType.LIGHT))
                .add_xaxis(xaxis_data=df_forecastDays.index.to_list())
                .add_yaxis(series_name="High Temperature",
                           y_axis=df_forecastDays[Temp_emo].apply(lambda x: int(x.replace('°C', '').split('~')[1])))
                .add_yaxis(series_name="Low Temperature",
                           y_axis=df_forecastDays[Temp_emo].apply(lambda x: int(x.replace('°C', '').split('~')[0])))
                .set_global_opts(
                title_opts=opts.TitleOpts(title="7 Days Forecast"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(type_="value", axislabel_opts=opts.LabelOpts(formatter="{value} °C")),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")

            )
                .set_series_opts(label_opts=opts.LabelOpts(formatter=JsCode("function(x){return x.data[1] + '°C';}")))
        )
        t = Timeline(
            init_opts=opts.InitOpts(theme=eval(f'ThemeType.{options}')))
        t.add_schema(play_interval=10000)
        t.add(c1, "24 Hours Forecast")
        t.add(c2, "7 Days Forecast")
        components.html(t.render_embed(), width=1000, height=520)  # 调整大小

        df = get_chart_data(chart)
        with st.expander("24 Hours Forecast Data"):
            st.table(
                df_forecastHours.style.format({'Temperature': '{}°C', 'Body Temperature': '{}°C', 'Humidity': '{}%'}))
        with st.expander("7 Days Forecast Data", expanded=True):  # 默认为展开
            st.table(df_forecastDays)
        st.markdown(f'### {chart} Chart')
        if chart == 'Pyechart':
            st_echarts(options=df)
        elif chart == 'Altair':
            eval(f'st.{charts_mapping[chart]}')(df, use_container_width=True)
        elif chart=='Map':
            eval(f'st.{charts_mapping[chart]}')(df,zoom=6)
        else:
            eval(f'st.{charts_mapping[chart]}')(df)

    col1, col2 = st.columns(2)
    video1, video2 = get_video_bytes()
    st.markdown('### 粉色海洋mv')
    col1.video(video1, format='video/mp4')
    st.markdown('### MOjito mv')
    col2.video(video2, format='video/mp4', start_time=2)


# class MyRandom:
#     def __init__(self, num):
#         self.random_num = num
#
#
# def my_hash_func(my_random):
#     num = my_random.random_num
#     return num


# """播放音乐(返回音乐文件的二进制字节）"""
def get_audio_bytes(music):
    audio_file = open(f'周杰伦 - {music}.mp3', 'rb')
    audio_bytes = audio_file.read()
    audio_file.close()
    return audio_bytes


@st.experimental_singleton
def get_video_bytes():
    video_file = open(f'周杰伦 - 粉色海洋.mp4', 'rb')
    video_bytes1 = video_file.read()
    video_file.close()
    video_file = open(f'周杰伦 - Mojito.mp4', 'rb')
    video_bytes2 = video_file.read()
    video_file.close()
    return video_bytes1, video_bytes2


@st.cache(allow_output_mutation=True, ttl=3600)
def get_chart_data(chart):
    data = np.random.randn(20, 3)
    df = pd.DataFrame(data, columns=['A', 'B', 'C'])
    if chart in ['Line', 'Bar', 'Area']:
        return df

    elif chart == 'Hist':
        arr = np.random.normal(1, 1, size=100)
        fig, ax = plt.subplots()
        ax.hist(arr, bins=20)
        return fig

    elif chart == 'Altair':
        df = pd.DataFrame(np.random.randn(200, 3), columns=['a', 'b', 'c'])
        c = alt.Chart(df).mark_circle().encode(x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
        return c

    elif chart == 'Map':
        df = pd.DataFrame(np.random.randn(100, 2) / [50, 50] + [23.08, 113.30], columns=['lat', 'lon'])
        return df

    elif chart == 'Graphviz':
        graph = graphviz.Digraph()
        graph.edge('grandfather', 'father')
        graph.edge('grandmother', 'father')
        graph.edge('maternal grandfather', 'mother')
        graph.edge('maternal grandmother', 'mother')
        graph.edge('father', 'brother')
        graph.edge('mother', 'brother')
        graph.edge('father', 'me')
        graph.edge('mother', 'me')
        graph.edge('brother', 'nephew')
        graph.edge('Sister-in-law', 'nephew')
        graph.edge('brother', 'niece')
        graph.edge('Sister-in-law', 'niece')
        graph.edge('me', 'son')
        graph.edge('me', 'daughter')
        graph.edge('where my wife?', 'son')
        graph.edge('where my wife?', 'daughter')
        return graph

    elif chart == 'Pyechart':
        options = {
            "xAxis": {
                "type": "category",
                "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            },
            "yAxis": {"type": "value"},
            "series": [
                {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}
            ],
        }
        return options


def weather_emoji(x):
    if '晴' in x:
        return emoji.emojize(':sun:')
    if '云' in x or '阴' in x:
        return emoji.emojize(':cloud:')
    if '雪' in x:
        return emoji.emojize(':snowflake:')
    if '雨' in x:
        return emoji.emojize(':umbrella:')
    else:
        return ''


@st.cache(ttl=3600)
def get_city_mapping():
    url = 'https://h5ctywhr.api.moji.com/weatherthird/cityList'
    r = requests.get(url)
    data = r.json()
    city_mapping = dict()
    guangzhou = 0
    flag = True
    for i in data.values():
        for each in i:
            city_mapping[each['name']] = each['cityId']
            if each['name'] != '广州市' and flag:
                guangzhou += 1
            else:
                flag = False

    return city_mapping, guangzhou



@st.cache(ttl=3600)
def get_city_weather(cityId):
    url = 'https://h5ctywhr.api.moji.com/weatherDetail'
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    data = {"cityId": cityId, "cityType": 0}
    r = requests.post(url, headers=headers, json=data)
    result = r.json()

    # today forecast
    forecastToday = dict(
        humidity=f"{result['condition']['humidity']}%",
        temp=f"{result['condition']['temp']}°C",
        realFeel=f"{result['condition']['realFeel']}°C",
        weather=result['condition']['weather'],
        wind=f"{result['condition']['windDir']}{result['condition']['windLevel']}级",
        updateTime=(datetime.datetime.fromtimestamp(result['condition']['updateTime']) + datetime.timedelta(
            hours=8)).strftime('%H:%M:%S')
    )




    # 24 hours forecast
    forecastHours = []
    for i in result['forecastHours']['forecastHour']:
        tmp = {}
        tmp['PredictTime'] = (datetime.datetime.fromtimestamp(i['predictTime']) + datetime.timedelta(hours=8)).strftime(
            '%H:%M')
        tmp[Temp_emo] = i['temp']
        tmp[BodyTemp_emo] = i['realFeel']
        tmp[Humidity_emo] = i['humidity']
        tmp[Weather_emo] = i['weather'] + weather_emoji(i['weather'])
        tmp[Wind_emo] = f"{i['windDesc']}{i['windLevel']}级"
        forecastHours.append(tmp)
    df_forecastHours = pd.DataFrame(forecastHours).set_index('PredictTime')



    # 7 days forecast
    forecastDays = []
    day_format = {1: '昨天', 0: '今天', -1: '明天', -2: '后天'}
    for i in result['forecastDays']['forecastDay']:
        tmp = {}
        now = datetime.datetime.fromtimestamp(i['predictDate']) + datetime.timedelta(hours=8)
        diff = (st.session_state.date_time - now).days
        festival = i['festival']
        tmp['PredictDate'] = (day_format[diff] if diff in day_format else now.strftime('%m/%d')) + (
            f' {festival}' if festival != '' else '')
        tmp[emoji.emojize('Temperature'+':sunflower:')] = f"{i['tempLow']}~{i['tempHigh']}°C"
        tmp[Humidity_emo] = f"{i['humidity']}%"
        tmp[Weather_day_emo] = i['weatherDay'] + weather_emoji(i['weatherDay'])
        tmp[Weather_night__emo] = i['weatherNight'] + weather_emoji(i['weatherNight'])
        tmp[Wind_day_emo] = f"{i['windDirDay']}{i['windLevelDay']}级"
        tmp[Wind_night_emo] = f"{i['windDirNight']}{i['windLevelNight']}级"
        forecastDays.append(tmp)
    df_forecastDays = pd.DataFrame(forecastDays).set_index('PredictDate')
    return forecastToday, df_forecastHours, df_forecastDays


if __name__ == '__main__':
    main()
