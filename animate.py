# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:30:21 2020

@author: ng253
"""
import pandas as pd
#importing libraries
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.animation as animation
import os #Need to create tem directory 


def connectpoints( x, y, p1, p2):
    x1, x2 = x[p1], x[p2]
    y1, y2 = y[p1], y[p2]
    ax1.plot([x1,x2],[y1,y2],'b--')
 
def animate(i):
        
    filename = "temp/NwSim"+ '.csv'
    df_flows = pd.read_csv(filename)
    if 'node_id' in df_nodes.columns:
        print("Generating plot network...")
    else:
        df_nodes.insert(0,'node_id',df_nodes.index)
    #ax1.figure(figsize=(15,15))
    plt.cla()
    ax1.clear()
    c2 =(df_flows.sort_values(by=['Minutes'],ascending=False) )[0:1]
    c3 = c2.melt(id_vars='Minutes', var_name='node_id',value_name='IsOccupied')
    
    c3 = c3.iloc[1:,1:]
    lines = df_edges.shape[0]
    for i in range(lines):
        connectpoints(df_nodes.x, df_nodes.y, df_edges.fr[i], df_edges.to[i])
    
    df_nodes.node_id = df_nodes.node_id.astype(int)
    c3.node_id = c3.node_id.astype(int)
    join_c3_nodes = pd.merge(c3, df_nodes,left_on='node_id', right_on = 'node_id')
    groups = join_c3_nodes.groupby('IsOccupied')
    for name, group in groups:
        if name == 0:
            cn="green"
        else:
            cn ="red"
        ax1.plot(group.x, group.y, marker='o', linestyle='', ms=5, color=cn)
   # ax1.tight_layout()

def getNodesWithMultiOptions(numArr):
    uniqueValues , indicesList, occurCount= np.unique(numArr.fr, return_index=True, return_counts=True)
    return(uniqueValues[occurCount >1])
# Method to get nodes array with cirtain status    
def getNodesForStatus(numArr, IsOccupied=1):
    ''' Returns the indexes of all occurrences of give element in
    the edges '''
    nodeIndexList = []
   
    for i in range(len(numArr)): 
        if numArr[i] == IsOccupied:
            nodeIndexList.append(i)
        
    return nodeIndexList   



plt.style.use('fivethirtyeight')

fig = plt.figure()
#creating a subplot 
ax1 = fig.add_subplot(1,1,1)

df_edges = pd.read_csv("edges.csv")
df_edges.rename(columns={'from':'fr'}, inplace=True)
#as from is key word creating problem in processing let's rename it 

df_nodes = pd.read_csv("nodes.csv")  
if os.path.isdir('./temp') == False:
    os.mkdir("temp")
df_multi_opt_nodes = getNodesWithMultiOptions(df_edges)

#plot_network(1)

ani= animation.FuncAnimation(fig,animate, interval=1000)

#plt.tight_layout()
plt.show()


    