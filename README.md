🏛️ 加州地震时空演化与风险管理监测平台
Spatiotemporal Evolution and Risk Management Platform for California Seismic Activity (1926-2026)

[![Research Tool](https://img.shields.io/badge/Research-Digital_Lab-blue.svg)](https://cal-quake-lab-v3.streamlit.app)
[![Data Source](https://img.shields.io/badge/Data-USGS_API-red.svg)](https://earthquake.usgs.gov/)

🔬 研究背景与学术价值 | Research Background
本项目基于应急管理 (Emergency Management) 与风险控制 (Risk Control) 理论，利用加州百年地震观测大数据，构建了一个动态的可视化分析模型。

在学术层面，本项目探索了以下维度：
1. 时空聚集性分析：通过交互式筛选，观察地震频次在南加州（如尔湾周边断层带）与北加州之间的演变规律。
2. 震级频数分布规律：基于 Gutenberg-Richter 定律，直观呈现不同等级地震的发生概率。
3. 管理决策支持：为城市韧性建设、绿色供应链中的物流风险评估提供直观的空间数据支撑。

📊 技术架构与数据治理 | Technical Architecture
* 数据层：实时调用 USGS (United States Geological Survey) 的 GeoJSON 结构化 API，确保研究的时效性与权威性。
* 处理层：采用 Python Pandas 进行清洗，统一 UTC 时间戳并进行多维特征工程（时、分、秒、年份、经纬度及深度）。
* 展示层：基于 Plotly Mapbox 构建高分辨率空间图层，支持 M4.0+ 级以上高震级事件的精准定位。

 🛠️ 核心功能组件 | Key Modules
* 指标面板 (KPI Metrics)：自动化提取观测周期内的统计特征，包括活跃年份识别与震级均值偏离。
* 多维过滤器：支持滑动年份区间（100年跨度）与震级阈值（4.0-9.0级）的组合查询。
* 科研数据共享 (Data Export)：提供标准化的 CSV 导出接口，支持将筛选后的数据集快速导入 SPSS, R 或 Python 进行高级计量经济学分析。

 🎓 访问学者成果说明
本项目系武汉理工大学与 Cal Poly 访问学者 (Visiting Scholar) 数字化实验室研究成果的一部分。
* 研究员: Yun Chen, Associate Professor, Ph.D.
* 研究方向: 绿色供应链、应急管理、创新管理。

在线演示地址: [https://cal-quake-lab-v3.streamlit.app](https://cal-quake-lab-v3.streamlit.app)
