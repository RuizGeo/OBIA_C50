
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 14:37:01 2015

@author: ruiz
"""
import gdal
import numpy as np
from skimage import measure 
import time
import csv
import profile
inicio=time.time()

"""Arquivo csv"""
file_csv= open('file_path.csv','wt')
writer_csv = csv.writer(file_csv,delimiter='\t',)
writer_csv.writerow(('fid','difMeanB1','difMeanB2','difMeanB3' ))

"""Leitura da imagem segmentada utilizando GDAL"""
#Pasta da imagems segmentada
file_seg = 'segmentacao.tif'
file_img= 'raster.tif'
#Obter bandas da imagem
#Abrir imagem    
gdal.AllRegister()
ds_img = gdal.Open(file_img, gdal.GA_ReadOnly)
#Dtype
d_type=({'names':[],'formats':[]})
d_typeMeanSeg=({'names':[],'formats':[]})
#numero de bandas
n_bands = ds_img.RasterCount
for n in xrange(n_bands):
    d_type['names'].append( 'band'+str(n+1))
    d_type['formats'].append('i16')
    d_typeMeanSeg['names'].append( 'meanBand'+str(n+1))
    d_typeMeanSeg['formats'].append('f16')
    
#insert value of segment
d_typeMeanSeg['names'].append( 'valueSeg')
d_typeMeanSeg['formats'].append('i32')

print d_type
print '  n_bands: ', n_bands
#Ler informacoes da imagem
colunas = ds_img.RasterXSize
linhas = ds_img.RasterYSize
#Inicar array bands
#arrayShape=ds_img.GetRasterBand(1).ReadAsArray().shape
recArrayBand = np.recarray((linhas,colunas),dtype=d_type)
#Ler mais que uma banda
if n_bands > 1:
    #create recarray bands
    for i in xrange(n_bands-1):
        print d_type['names'][i]
        
        recArrayBand[d_type['names'][i]]= ds_img.GetRasterBand(i+1).ReadAsArray()
        print 'min: ',np.min(recArrayBand[d_type['names'][i]])
        print 'max: ',np.max(recArrayBand[d_type['names'][i]])
        print "d_type['names'][i]: ", recArrayBand[d_type['names'][i]]      
    
else:
    #create recarray bands    
    recArrayBand[d_type['names'][0]]= ds_img.GetRasterBand(1).ReadAsArray().astype(np.int8)
    #band = ds_img.GetRasterBand(1).ReadAsArray().astype(np.int8)
    #arrayBands = np.recarray(band, formats='i8',names=nomes)
    #arrayBands[nomes.split(',')[0]]=band

#Obter drives para todos os tipos de imagem
gdal.AllRegister()
ds = gdal.Open(file_seg, gdal.GA_ReadOnly)
#converter banda para raster 
segmentacao = ds.GetRasterBand(1).ReadAsArray().astype(np.int32)
print 'segmentacao: ',segmentacao.shape
print "recArrayBand[d_type['names'][i]: ",recArrayBand[d_type['names'][0]].shape
print '(linhas*colunas): ',(linhas*colunas)

#Obter regioes
regiao_seg=measure.regionprops(segmentacao)
v_max= segmentacao.max()
#Array segmentos
recMeanBandSeg = np.recarray(v_max,dtype=d_typeMeanSeg)
#Loop regprop
for id_seg, regprop in enumerate(regiao_seg):
    for id_name,n in enumerate(d_typeMeanSeg['names'][0:-1]):
    
        #Rec values means regions
        recMeanBandSeg[id_seg][n] = np.round(np.mean(recArrayBand[d_type['names'][id_name]][np.asarray(regprop.coords[:,0]),np.asarray(regprop.coords[:,1])]),3)
        #Get value seg
      
    #Rec value segment
    recMeanBandSeg[id_seg][d_typeMeanSeg['names'][-1]] = segmentacao[regprop.coords[0,0],regprop.coords[0,1]]
    
    
print "recMeanBandSeg['meanBand1']: ",recMeanBandSeg['meanBand1']
#Percorrer regioes
for i, regprop in enumerate(regiao_seg):
    uniqueValues =np.array([])
    #Inserir -99 nos valores iguais a zero e iguais ao maior valor da linha e coluna
    rows= np.where( np.asarray(regprop.coords[:,0]) == segmentacao.shape[0]-1,-99,np.asarray(regprop.coords[:,0]))
    rows= np.where( rows == 0, -99,rows) 
    cols= np.where( np.asarray(regprop.coords[:,1]) == segmentacao.shape[1]-1,-99,np.asarray(regprop.coords[:,1]))
    cols= np.where( cols == 0, -99,cols)
    indices=np.column_stack((rows,cols))
    print i
    
    #Deletar os pares de coordenadas que contem -99
    indices=np.delete(indices,np.where(indices==-99)[0],0) 
    #Get values neighbors
    uniqueValues =np.append(uniqueValues,np.unique(segmentacao[indices[:,0]-1,indices[:,1]-1]))
    uniqueValues =np.append(uniqueValues,np.unique(segmentacao[indices[:,0]+1,indices[:,1]+1]))
    uniqueValues =np.append(uniqueValues,np.unique(segmentacao[indices[:,0]-1,indices[:,1]+1]))
    uniqueValues =np.append(uniqueValues,np.unique(segmentacao[indices[:,0]+1,indices[:,1]-1]))
    unique=np.unique(uniqueValues).astype(np.int32)
    #Calculate diff mean neighbors   
    b1=np.sum(recMeanBandSeg['meanBand1'][np.in1d(recMeanBandSeg['valueSeg'],unique)]- recMeanBandSeg[i]['meanBand1'])/unique.shape[0]-1
    b2=np.sum(recMeanBandSeg['meanBand2'][np.in1d(recMeanBandSeg['valueSeg'],unique)]- recMeanBandSeg[i]['meanBand2'])/unique.shape[0]-1
    b3=np.sum(recMeanBandSeg['meanBand3'][np.in1d(recMeanBandSeg['valueSeg'],unique)]- recMeanBandSeg[i]['meanBand3'])/unique.shape[0]-1
    writer_csv.writerow((i+1,round(b1,2),round(b2,2),round(b3,2)))
file_csv.close()

fim=time.time()
print fim-inicio

        
