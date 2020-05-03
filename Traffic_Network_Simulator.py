# -*- coding: utf-8 -*-
"""
# Project assignment
# Submitted by - Nitin Kumar Garg - 2508212G@student.gla.ac.uk
# Deadline- Monday, January 27th, 10am (UK time).


"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from csv import writer
import random
import time  
import os,shutil #Need to create tem directory 

#************************************************************
class Network:
    
    #Network class constructor, takes egdes and node files
    def __init__(self, nodesCSVfile, edgesCSVfile):
        self.df_edges = pd.read_csv(edgesCSVfile)
        self.df_edges.rename(columns={'from':'fr'}, inplace=True)
        #as from is key word creating problem in processing let's rename it 
        
        self.df_nodes = pd.read_csv(nodesCSVfile)  
        if os.path.isdir('./temp') == False:
            os.mkdir("temp")
        self.df_multi_opt_nodes = self.getNodesWithMultiOptions(self.df_edges)
        self.df_flows = pd.DataFrame() # to be populated first
        self.df_flowplot =  pd.DataFrame() # to be populated for plot flow 
    
    #plot flow plot
    def plot_flow(self, segment):
        self.checkAndReadProcessedData()
       # df_plot = pd.read_csv("flow_6202.csv")
        a = np.array(segment)
        se = a.astype(str)
        
        plotData = (self.df_flowplot.groupby(["Minutes"]).sum()).loc[:, se]
           # print(flowData)a
        fig = plt.figure(figsize=(12,8))
        fig.suptitle('Flow', fontsize=20)
        plt.xlabel('Minutes', fontsize=18)
        plt.ylabel('Flow', fontsize=16)
        plt.plot(plotData,label=["1","2"])
        plt.show()
      
    #plot occupancy plot
    def plot_occupancy(self, segment):
        self.checkAndReadProcessedData()
        a = np.array(segment)
        se = a.astype(str)
        countData = (self.df_flows.groupby(["Minutes"]).count()).loc[:, se]
        flowData = (self.df_flows.groupby(["Minutes"]).sum()).loc[:, se]
        
        occupancy = flowData/countData
        fig = plt.figure(figsize=(12,8))
        fig.suptitle('Occupancy', fontsize=20)
        plt.xlabel('Minutes', fontsize=18)
        plt.ylabel('Occupancy', fontsize=16)
        plt.plot(occupancy)
        plt.show()
    
    #plot fundamental plot
    def plot_fundamental_diagram(self, minute):
        self.checkAndReadProcessedData()
        c2 =(self.df_flows.sort_values(by=['Minutes'],ascending=False) )[0:1]
        maxMinAvailable= c2['Minutes'].to_numpy()[0]
        if (minute <= maxMinAvailable):
            countData = (self.df_flows.groupby(["Minutes"]).count()).iloc[minute,1:]
            flowData = (self.df_flows.groupby(["Minutes"]).sum()).iloc[minute,1:]
            occupancy = flowData/countData
            plotData = (self.df_flowplot.groupby(["Minutes"]).sum()).iloc[minute,1:]
         
            fig = plt.figure(figsize=(12,8))
            fig.suptitle('Fundamental Diagram', fontsize=20)
            plt.xlabel('Occupancy', fontsize=18)
            plt.ylabel('Flow', fontsize=16)
            plt.scatter(occupancy,plotData)
            plt.show()
        else:
            print("Please call fundamental diagram for lesser then {} minute".format(maxMinAvailable))
    
    # draw the line 
    def connectpoints(self, x, y, p1, p2):
        x1, x2 = x[p1], x[p2]
        y1, y2 = y[p1], y[p2]
        plt.plot([x1,x2],[y1,y2],'b--')
    
    #draw segment points with color and call function to draw lines 
    def plot_network(self):
        
        self.checkAndReadProcessedData()
        if 'node_id' in self.df_nodes.columns:
            print("Generating plot network...")
        else:
            self.df_nodes.insert(0,'node_id',self.df_nodes.index)
        plt.figure(figsize=(15,15))
        c2 =(self.df_flows.sort_values(by=['Minutes'],ascending=False) )[0:1]
        c3 = c2.melt(id_vars='Minutes', var_name='node_id',value_name='IsOccupied')
        
        c3 = c3.iloc[1:,1:]
        lines = self.df_edges.shape[0]
        for i in range(lines):
            self.connectpoints(self.df_nodes.x, self.df_nodes.y, self.df_edges.fr[i], self.df_edges.to[i])
        
        self.df_nodes.node_id = self.df_nodes.node_id.astype(int)
        c3.node_id = c3.node_id.astype(int)
        join_c3_nodes = pd.merge(c3, self.df_nodes,left_on='node_id', right_on = 'node_id')
        groups = join_c3_nodes.groupby('IsOccupied')
        for name, group in groups:
            if name == 0:
                cn="green"
            else:
                cn ="red"
            plt.plot(group.x, group.y, marker='o', linestyle='', ms=5, color=cn)
    
    # Read the node ids and create CSV header, it provides flexibility to the solution
    def get_CSV_Headers(self):
        if 'node_id' in self.df_nodes.columns:
            print("Gathering information..")
        else:
            self.df_nodes.insert(0,'node_id', self.df_nodes.index)
        
        node_ids_rw = np.array(self.df_nodes.iloc[:,0])
        node_ids_str = node_ids_rw.astype(str)
        init_header = np.array(['Minutes', 'Seconds'])
        csv_file_headers = np.concatenate((init_header,node_ids_str))
        
        return (csv_file_headers)
    
    # run the simulation for minutes and for each second,
    # call birth and deth methods
    # call flow method to move cars from occupied segments
    # call method to Generates the data for run and creates flow data for analysis
    
    def run(self, minutes=30, p_birth = 0.001, p_death = 0.001):
        
        folder = './temp'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete previous data %s. Reason: %s' % (file_path, e))        

         
        filename = "temp/NwSim"+ '.csv'
        csv_file_headers = self.get_CSV_Headers()
        
        row_array_data = np.zeros((csv_file_headers.shape[0],), dtype=int)
        #print(row_array_data)
        print(filename)
        with open(filename, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(csv_file_headers)
          #  csv_writer.writerow(row_array_data[0])
            
        for i in range(minutes):
            with open(filename, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
                csv_writer = writer(write_obj)
               
                row_array_data[0] = i +1
                for j in range(60):
                    print("Simulation time {} minutes, {} seconds".format(i,j))
                    row_array_data[1] = j +1
                    row_array_data = self.BirthOrDeath_of_car(row_array_data, p_birth, IsBirth = True )
                    row_array_data = self.BirthOrDeath_of_car(row_array_data, p_death, IsBirth = False)
                    row_array_data = self.flowingTraffic(row_array_data)
                    csv_writer.writerow(row_array_data)
                    #print("This will be returned")
        print(filename)
        #self.df_flows = pd.read_csv(filename)
       
        return(row_array_data)
    
    #Checks if the user is trying to draw the plots with previously saved run data  
    def checkAndReadProcessedData(self):
        if self.df_flows.empty :
            filename = "temp/NwSim"+ '.csv'
            self.df_flows = pd.read_csv(filename)
#        #print(self.df_flows)
        if self.df_flowplot.empty :
            filename2 = "temp/flow"+ '.csv'
            if os.path.exists(filename2):
                os.remove(filename2)
            filename2 = self.processing_plotflowdata()
            self.df_flowplot = pd.read_csv(filename2) 
    
    # Generates the data for run and creates flow data for analysis
    def processing_plotflowdata(self):
        #self.df_flowplot = pd.read_csv(flowCSVfile)
       # checkAndReadProcessedData()
        
        c2 =(self.df_flows.sort_values(by=['Minutes'],ascending=False) )[0:1]
        maxMinAvailable= c2['Minutes'].to_numpy()[0]
        
        filename = "temp/flow"+ '.csv'
        csv_file_headers = self.get_CSV_Headers()
        
        with open(filename, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(csv_file_headers)
            for i in range(maxMinAvailable):
                flowdata = self.df_flows[self.df_flows.iloc[:,0]==i+1]
                nodes = len(flowdata.iloc[0,2:])
                row_data = np.zeros((nodes+2,), dtype=int)
                row_data[0] = i+1
                row_data[1] = i+1
                
                for j in range(nodes):
                    x = pd.Series(flowdata.iloc[:,2+j].astype(str)).str.cat(sep='')
                    count = x.count('10')
                    row_data[2+j] = count
                csv_writer.writerow(row_data)
            
            time.sleep(5)
           # self.df_flowplot = pd.read_csv(filename)      
        return(filename)
        
    #Metod responsible for birth or death of the car 
    def BirthOrDeath_of_car(self, probs, alfa=.001, IsBirth = True):
        index = 2
        while(index < len(probs)):
            if(probs[index] != IsBirth):
                r = random.random()
                #print(r) 
                if (alfa > r):
                    probs[index] = IsBirth
                    if(IsBirth):
                        print(".........Car has ENTERED (Birth) at segment {}".format(index))
                    else:
                        print("*********Car has EXITED (Death) at segment {}".format(index))
       
            index += 1
        
        return(probs)
    
    #Method responsible for traffic flow 
    def flowingTraffic(self, probs):
        # choose occupied rendomly -> ANS1
        probs_c = probs[2:] # remove first 2 items 
        occuNodesIndexList = self.getNodesForStatus(probs_c, IsOccupied=1)
        for fromMoveIndex in random.sample(list(occuNodesIndexList), len(occuNodesIndexList)):
            to_options = (self.df_edges.loc[self.df_edges['fr'] == fromMoveIndex]["to"]).to_numpy()
             # check if it has 2 or more options
            if (len(to_options)>1):
                #get it's options
                #if it has 2 options decied where to go A or B or .. -> ANS2
                toMoveIndexIfAvailable = random.choice(to_options)
               # print('Car is choosing option {0} if it is available.'.format(IndexToMoveIfAvailable))
              #  print("I am having option -- Plan A/B")
            else:
    #        # Check if it can go to 1 place only -> ANS 2
                toMoveIndexIfAvailable = to_options
              # if ANS2 is unoccupied run 
            
            if(probs_c[toMoveIndexIfAvailable] == 0):
                probs_c[toMoveIndexIfAvailable] = 1
                probs_c[fromMoveIndex] = 0
             #   print('Car moved from {0} to {1}.'.format(fromMoveIndex, toMoveIndexIfAvailable )) 
        
        probs[2:] = probs_c
        return (probs)
    # Method used for populating nodes having road divisions 
    def getNodesWithMultiOptions(self, numArr):
        uniqueValues , indicesList, occurCount= np.unique(numArr.fr, return_index=True, return_counts=True)
        return(uniqueValues[occurCount >1])
    # Method to get nodes array with cirtain status    
    def getNodesForStatus(self, numArr, IsOccupied=1):
        ''' Returns the indexes of all occurrences of give element in
        the edges '''
        nodeIndexList = []
       
        for i in range(len(numArr)): 
            if numArr[i] == IsOccupied:
                nodeIndexList.append(i)
            
        return nodeIndexList   
    
#************************************************************
#Test Network simolator class
        
n = Network("nodes.csv","edges.csv")
n.run(minutes=11,p_birth = 0.001, p_death = 0.001)
n.plot_network()
n.plot_flow(segment=[50,425])
n.plot_occupancy(segment=[50,425])
for i in range(10):
    n.plot_fundamental_diagram(minute=i)

