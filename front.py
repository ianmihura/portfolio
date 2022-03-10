import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt

from analysis import Portfolio_Analysis
import file_io as IO
import finance

st.set_page_config(
    page_title="Portfolio",
    page_icon="chart_with_upwards_trend"
)

p = IO.read_portfolio()
a = Portfolio_Analysis(p)

fig, ax = plt.subplots()
plt.scatter(a.df_meta['return_std'], a.df_meta['return_mean'])
plt.scatter(a.standard_deviation_p, a.mean_return_p)
ax.annotate('P', (a.standard_deviation_p, a.mean_return_p))
for i, text in enumerate(a.assets):
    ax.annotate(text, (a.df_meta['return_std'][i], a.df_meta['return_mean'][i]))
ax.set_xlabel('standard deviation')
ax.set_ylabel('mean return')

st.title('Portfolio')
st.bar_chart(a.df_meta['assets_per'])

st.title('Metadata')
st.write(a.df_meta)

st.title('Data')
st.write(a.df)

st.title('Correlation matrix')
st.write(a.df_correl_matrix)
st.title('Optimization')
(res, sharper) = finance.optimize_p(a.df_meta['assets_per'], a.df_meta['return_mean'], a.df_covar_matrix)
st.write('Optimized portfolio', pd.DataFrame(zip(res, a.df_meta['assets_per']), index=a.assets, columns=['new', 'old']))
st.write(pd.DataFrame((sharper, a.sharper_ratio), index=['new','old'], columns=['Sharper ratio']))
op_std = finance.standard_deviation_p(res, a.df_covar_matrix)
op_mean = finance.mean_return_p(res, a.df_meta['return_mean'])
st.write(pd.DataFrame((op_mean, a.mean_return_p), index=['new','old'], columns=['Mean return']))
st.write(pd.DataFrame((op_std, a.standard_deviation_p), index=['new','old'], columns=['Standard deviation']))

plt.scatter(op_std, op_mean)
ax.annotate('*P', (op_std, op_mean))

st.write(fig)