def checkperformance(predict,real):
    diffpredict=[]
    diffreal=[]
    correct=0
    for i in range(len(predict)-1):
        diffpredict.append(predict[i+1]-predict[i])
        diffreal.append(real[i+1]-real[i])
    for i in range(len(diffreal)):
        if diffreal[i]>=0 and diffpredict[i]>=0:
            correct=correct+1
        elif diffreal[i]<0 and diffpredict[i]<0:
            correct=correct+1
        else:
            continue
    return correct/(len(diffreal)-1)