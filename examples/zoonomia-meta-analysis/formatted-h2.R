library(rmeta)

meta_sldsc <- function (myrow,dir,analysis,mytraits=traits,mysd=""){
  nbtrait = length(mytraits)
  M    = 5961159
  res   = NULL
  for (t in mytraits){
    data     = read.table(paste(dir,"/",t,".",analysis,".results",sep=""),h=T)[myrow,]
    log     = read.table(paste(dir,"/",t,".",analysis,".log",sep=""),h=F,fill=T)
    h2g     = as.numeric(as.character(log[which(log$V4=="h2:"),5]))
    #
    myenrstat  = (h2g/M)*((data$Prop._h2/data$Prop._SNPs)-(1-data$Prop._h2)/(1-data$Prop._SNPs)) #step 1
	  myenrstat_z = qnorm(data$Enrichment_p/2) #step2
	  myenrstat_sd = myenrstat/myenrstat_z #step3
	  data     = cbind(data, myenrstat, myenrstat_sd)
    #
    if (mysd==""){ #particular case of binary annotation, where sd=sqrt(p(1-p))
      data$Coefficient      = M * sqrt(data$Prop._SNPs*(1-data$Prop._SNPs)) * data$Coefficient      / h2g
      data$Coefficient_std_error = M * sqrt(data$Prop._SNPs*(1-data$Prop._SNPs)) * data$Coefficient_std_error / h2g
    } else {
      data$Coefficient      = M * mysd * data$Coefficient      / h2g
      data$Coefficient_std_error = M * mysd * data$Coefficient_std_error / h2g
    }
    #
    res     = rbind(res,data)
  }
  res = data.frame(res)
  test0 = meta.summaries(res$Prop._h2  , res$Prop._h2_std_error  , method="random")
  test1 = meta.summaries(res$Enrichment , res$Enrichment_std_error , method="random")
  test2 = meta.summaries(res$myenrstat  , res$myenrstat_sd     , method="random")
  test3 = meta.summaries(res$Coefficient , res$Coefficient_std_error , method="random")
  out = rbind(c(mean(res$Prop._SNPs),test0$summary, test0$se.summary, test1$summary, test1$se.summary, 2*pnorm(-abs(test2$summary/test2$se.summary)), test3$summary, test3$se.summary, 2*pnorm(-abs(test3$summary/test3$se.summary))))
  colnames(out) = c("propsnps","proph2","proph2_se","Enr","Enr_se","Enr_P","tau","tau_se","tau_P")
  rownames(out) = data$Category[1]
  out
}

meta_sldsc(%d, "%s", "baselineLD_mammal", c(%s))
