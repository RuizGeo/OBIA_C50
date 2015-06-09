#impotar bibliotecas
library(C50)
library(maptools)
library(caret)
library(plyr)
library(e1071)
library(ggplot2)
library(base)
library(psych)
#leitura do arquivo shape amostras
shape = readShapePoints("path_file.shp")
shape.test = readShapePoints("path_file.shp")
#leitura dos arauivos csv
textura = read.delim("path_file.csv", head=T)
espectral = read.table('path_file.csv',head=T)
geometrico = read.table('path_file.csv',head=T)
contextual = read.table('path_file.csv',head=T)
elev=read.table('path_file.csv',head=T)

#Calcular razao entre bandas
r_verde_azul = espectral$band2_mean/espectral$band3_mean
r_vermelho_azul = espectral$band1_mean/espectral$band3_mean
r_verd_verm = espectral$band2_mean/espectral$band1_mean
#Calcular ratio bands
ratio_R = espectral$band1_mean/(espectral$band1_mean+espectral$band2_mean+espectral$band3_mean)
ratio_G = espectral$band2_mean/(espectral$band1_mean+espectral$band2_mean+espectral$band3_mean)
ratio_B = espectral$band3_mean/(espectral$band1_mean+espectral$band2_mean+espectral$band3_mean)
razoes_bandas = data.frame(r_verde_azul,r_vermelho_azul,r_verd_verm,ratio_R,ratio_G,ratio_B)
#escrever CSV
write.table(razoes_bandas, file = "path_file.csv", sep='\t',col.names = NA)
#dados para classifiar
#dados =data.frame(espectral,contextual,geometrico,textura,elevacao,r_verde_azul,r_vermelho_azul,r_verd_verm,ratio_R,ratio_G,ratio_B )
#Remover colunas
textura= within(textura, rm(fid,band1,band2,band3))
geometrico= within(geometrico, rm(fid))
elev= within(elev, rm(fid))
espectral= within(espectral, rm(fid, band4_mean,band4_std))
contextual= within(contextual, rm(fid))
#Selecionar os segmentos de treinamento
classes= factor(as.integer(shape$id_classes))
data.trein = data.frame(espectral[c(shape$id_seg),],geometrico[c(shape$id_seg),],textura[c(shape$id_seg),],contextual[c(shape$id_seg),],elev[c(shape$id_seg),],razoes_bandas[c(shape$id_seg),])
data.test= data.frame(espectral[c(shape.test$id_seg),],geometrico[c(shape.test$id_seg),],textura[c(shape.test$id_seg),],contextual[c(shape.test$id_seg),],elev[c(shape.test$id_seg),],razoes_bandas[c(shape.test$id_seg),])
classes.test = factor(as.integer(shape.test$id_classe))


df = data.frame(win =logical(),trial=numeric(),minCase=numeric(),kappa=numeric(),var.kappa=numeric())
assessClassifyC50 = function(winnows,trial, min.Cases,data.train, train.classes,data.test,test.classes){
				  				  
				  for (w in seq (along=winnows)){
				      #print (winnows[w])
				      for (t in seq (along=trial)){
					  #print (trial[t]);
					  for (mc in seq (along=min.Cases)) {
					    
					    
					  model_tree = C5.0(data.trein,train.classes,trials=trial[t],control=C5.0Control(winnow=winnows[w],minCases = min.Cases[mc]))
					  predictTree = predict(model_tree,data.test);
					  #print (summary(predictTree))
					  accuracy =cohen.kappa(x=cbind(as.integer(predictTree),as.integer(test.classes)))
					df = rbind(df, data.frame(win = winnows[w],trial=trial[t],minCase=min.Cases[mc],kappa=accuracy$kappa,var.kappa=accuracy$var.weighted))
					  
					  } } }
					  return (df)}

df_model =assessClassifyC50(c(TRUE, FALSE),c(1,5,(1:10)*10),c(2, (1:10)*5),data.trein,classes,data.test,classes.test)
#salvar data.frame
saveRDS(df_model, file="path_file.Rda")

best_model = C5.0(data.trein,classes,trial=80,control=C5.0Control(winnow=FALSE,minCases=5))
cat(as.character(summary(best_model)),file="path_file.txt",append=TRUE)
help(cat)
