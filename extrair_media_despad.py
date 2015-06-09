# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 14:31:30 2015

@author: ruiz
"""
from skimage import measure
import csv
import gdal
import os
import numpy as np
from tempfile import TemporaryFile
outfile=TemporaryFile()
import time

ini=time.time()


#Funcao para criar lisa com os caminhos dos rasters
def get_imlist(path):
    """ Returns a list of filenames for
    all tif images in a directory. """
    return [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.tif')]

"""Percorrer o arquivos rasters e armazena-los em um recarray"""
#Pasta onde estao os rasters
path = 'C:/LuisFernando/Pesquisas/OBIA_C50/Rasters/orto/'
#Dict para adicionar os rasters
bandas_dic={}

files_attr = get_imlist(path)
print files_attr
for p in files_attr:
    print 'p: ',p
    #Obter nome do arquivo    
    nome = p.split('/')[-1].split('.')[0]  
    #Abrir imagem    
    gdal.AllRegister()
    ds = gdal.Open(p, gdal.GA_ReadOnly)
    #numero de bandas
    n_bands = ds.RasterCount
    #Ler mais que uma banda
    if n_bands > 1:
        for i in xrange(1, n_bands):       
            #converter banda para raster 
            band = ds.GetRasterBand(i).ReadAsArray()
            nome='band'+str(i)
            #criar dicionarios de arrays
            bandas_dic[nome]=band
            
    else:
        band = ds.GetRasterBand(1).ReadAsArray()
        #criar dicionarios de arrays
        bandas_dic[nome]=band
print nome,'\n', bandas_dic.keys()

"""Leitura da imagem segmentada utilizando GDAL"""
#Pasta da imagems segmentada
file_seg = 'C:/LuisFernando/Pesquisas/OBIA_C50/seg/seg_100/seg_15_100.tif'
#Obter drives para todos os tipos de imagem
gdal.AllRegister()
ds = gdal.Open(file_seg, gdal.GA_ReadOnly)
#converter banda para raster 
segmentacao = ds.GetRasterBand(1).ReadAsArray().astype(np.int32)
#Obter regioes
regiao_seg=measure.regionprops(segmentacao)
#Ler informacoes da imagem
geoTransform = ds.GetGeoTransform()
colunas = ds.RasterXSize
linhas = ds.RasterYSize
print nome,'\n', bandas_dic.keys()
#min e max valores do array
minValue= np.min(segmentacao)
maxValue = np.max(segmentacao)

colunas = []
colunas.append('fid')
for n in bandas_dic.keys():
    colunas.append(n+'_mean')
    colunas.append(n+'_StdDev')
                   
print 'colunas: ', colunas
file_csv= open('C:/LuisFernando/Pesquisas/OBIA_C50/espectral/100/seg_15_100_espec_A.csv','wt')
writer_csv = csv.writer(file_csv,delimiter='\t',)
writer_csv.writerow(tuple(colunas))
#Percorrer segmentacao
for i,regprop in enumerate(regiao_seg):
    print 'i :',i
    mean=[]
    mean.append(i+1)
    #Percorrer raster atributos
    for at in bandas_dic:
        #print 'bandas_dic[at][regprop.coords].shape ',bandas_dic[at][regprop.coords[0,0],regprop.coords[0,1]].shape
        mean.append(np.around(np.mean(bandas_dic[at][regprop.coords[:,0],regprop.coords[:,1]]),3))
        mean.append(np.around(np.std(bandas_dic[at][regprop.coords[:,0],regprop.coords[:,1]]),3))
        
    #Escrever valores no arquivo csv
    writer_csv.writerow(tuple(mean))
    

file_csv.close()

fim =time.time()
print fim-ini, ' segundos'
