#Written by Joseph Gallego Based on Ding's Paper: Convex and Semi-Nonnegative Matrix Factorizations
#This function finds the Matrix Factors W and G of K = KWG Where:
#     K is a kernel matrix of size NxN and K has a positive part denoted Ap and a negative part denoted An

#X is a features by samples matrix
import time
import os, sys
os.chdir(os.pardir)
os.chdir(os.pardir)
sys.path.append(os.getcwd())
import mkl
import numpy as np
import scipy.io as sio
from Algorithms.Python.computeKernelMatrix import computeKernelMatrix
from numbapro import autojit
import numbapro.cudalib.cublas.api as apblas


#if len(sys.argv) < 5:
#  print 'Use: nmfCoding.py Initial H, Inital W, Positive part of kernel, Negative part of kernel, iterations, '
#  sys.exit()

#@jit(argtypes=[double[:,:], double[:,:],double[:,:],double[:,:]])

def clusterKCNMF(X,option):
    [A,Y,numIter,finalResidual] = KCNMF(X,option)
    indCluster=np.argmax(Y,axis=0)
    indCluster=np.transpose(indCluster)
    return indCluster    
    
def KCNMF(X,option):
    
    X = np.array(X,dtype=float)
    
    Ak = computeKernelMatrix(X,X,option)   
    (Ap,An) = getPossitiveNegative(Ak)
    
    r,c = X.shape #c is # of samples, r is # of features
    
    G,W = initialization(X,c,option)
    
    XfitPrevious=np.inf
    
    #err = np.zeros(iterations)
    for i in np.arange(1,option['epocs']):
        #print 'Iteration: ', i
        [Ap,An,G,W] = __operations(Ap,An,G,W)
        
        A = W
        Y = np.transpose(G)
        if i % 10 == 0 or i+1 == option['epocs']:
            if option['dis']:
                print 'Iterating >>>>>> ' + str(i)
		print G
		print W
            XfitThis = np.dot(np.dot(Ak , A) , Y)
            fitRes = np.linalg.norm(XfitPrevious-XfitThis,ord= 'fro')
            XfitPrevious=XfitThis
            curRes = np.linalg.norm(Ak-XfitThis,ord= 'fro')
            if option['tof'] >= fitRes or option['residual'] >= curRes or i+1 == option['epocs']:
                print('Mutiple update rules based Kernel Convex-NMF successes! \n # of iterations is %0.0d. \n The final residual is %0.4d.',i,curRes);
                numIter = i
                finalResidual = curRes
    return [A,Y,numIter,finalResidual]

#@autojit(target="cpu") 
def __operations(Ap,An,G,W):
    ApW = apblas.np.dot(Ap,W)
    AnW = apblas.np.dot(An,W)
    GWt = apblas.np.dot(G,apblas.np.transpose(W))
    G = apblas.np.multiply(G,apblas.np.sqrt(apblas.np.divide((ApW+ apblas.np.dot(GWt,AnW)) , (AnW+apblas.np.dot(GWt,ApW)))))
    GtG = apblas.np.dot(apblas.np.transpose(G),G)
    W = apblas.np.multiply(W,apblas.np.sqrt(apblas.np.divide((apblas.np.dot(Ap,G)+ apblas.np.dot(AnW,GtG)) , (apblas.np.dot(An,G)+apblas.np.dot(ApW,GtG)))))   
    return Ap,An,G,W
    
#@autojit(target="cpu")    
def getPossitiveNegative(Ak):
    Ap = (apblas.np.abs(Ak) + Ak) / 2.
    An = (apblas.np.abs(Ak) - Ak) / 2.
    return Ap,An

@autojit(target="cpu") 
def initialization(X,c,param):
    if param['initialization'] == 'random':
         G=np.random.random((c,param['k']))
         W=np.random.random((c,param['k']))
    if param['initialization'] == 'deterministic':
         G=np.ones((c,param['k']))*0.2
         W=np.ones((c,param['k']))*0.2
    return G,W

def test():
    X = sio.loadmat('Datasets/AR.mat')['data']
    option = {}
    option['epocs']  = 1000
    option['param']  = 2
    option['tof']  = 2**-20
    option['residual'] = 2**-20
    option['kernel'] = 'rbf'
    option['initialization'] = 'random'
    option['k'] = 100
    option['dis'] = True
    start = time.clock()
    labels = clusterKCNMF(np.transpose(X),option)
    print (time.clock() - start)
    sio.savemat('labelsgpu',{'labels':labels})
    
test()
