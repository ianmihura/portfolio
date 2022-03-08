import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from analysis import Portfolio_Analysis
import file_io as IO
import finance

p = IO.read_portfolio()
a = Portfolio_Analysis(p)

fig, ax = plt.subplots()
plt.scatter(a.df_meta['return_std'], a.df_meta['return_mean'])
ax.set_xlabel('standard deviation')
ax.set_ylabel('mean return')
for i, text in enumerate(a.coins):
    ax.annotate(text, (a.df_meta['return_std'][i], a.df_meta['return_mean'][i]))
st.write(fig)

st.title('Portfolio')
st.bar_chart(a.df_meta['coins_per'])

st.title('Metadata')
st.write(a.df_meta)

st.title('Data')
st.write(a.df)

st.title('Correlation matrix')
st.write(a.df_correl_matrix)

st.title('Optimization')
(res, sharper) = finance.optimize_p(a.df_meta['coins_per'], a.df_meta['return_mean'], a.df_covar_matrix)
st.write('Optimized portfolio', pd.DataFrame(zip(res, a.df_meta['coins_per']), index=a.coins, columns=['new', 'old']))
st.write(pd.DataFrame((sharper, a.sharper_ratio), index=['new','old'], columns=['Sharper ratio']))
st.write(pd.DataFrame((finance.mean_return_p(res, a.df_meta['return_mean']), a.mean_return_p), index=['new','old'], columns=['Mean return']))
st.write(pd.DataFrame([finance.standard_deviation_p(res, a.df_covar_matrix), a.standard_deviation_p], index=['new','old'], columns=['Standard deviation']))