import numpy as np

MTEMP = 27      #celsius
MHUM  = 60      #percentage of humidity
MSOIL = 90      #percentage of soil humidity
MLUM  = 12      #UV index

STEMP = 0.3  #std
SHUM  = 1.0
SSOIL = 0.5
SLUM  = 0.3


LIMT = [5, -4]
LIMH = [10, -10]
LIMS = [5, -20]
LIML = [2, -2]

def gen_vector(normal=0,mean=0, std=1, size=30, lims=-1):
    seg1 = int(size*0.3)
    seg2 = size-seg1
    
    v = np.random.randn(size)*std + mean
    
    if normal!=0:
        temp = np.concatenate((np.linspace(0, lims, seg1), np.linspace(lims, 0, seg2)),axis=0)
        
        v+=temp
        
    #v[v>100]=100
    
    return v


def gen_complete_vector(normal, mean, std, limits):
    
    v = None

    if normal==0:
        v = gen_vector(0, mean, std, size=100, lims=limits)
    elif normal==1:
        v0 = gen_vector(0, mean, std, size=20, lims=limits[0])
        v1 = gen_vector(1, mean, std, size=60, lims=limits[0])
        v2 = gen_vector(0, mean, std, size=20, lims=limits[0])
        
        v=np.concatenate((v0,v1,v2))
        
    elif normal==2:
        v0 = gen_vector(0, mean, std, size=20, lims=limits[1])
        v1 = gen_vector(2, mean, std, size=60, lims=limits[1])
        v2 = gen_vector(0, mean, std, size=20, lims=limits[1])
        
        v=np.concatenate((v0,v1,v2))
    
    return v
    
def gen_temp_meas(normal):
    return gen_complete_vector(normal,MTEMP, STEMP, LIMT)

def gen_hum_meas(normal):
    return gen_complete_vector(normal,MHUM, SHUM, LIMH)

def gen_soil_meas(normal):
    return gen_complete_vector(normal,MSOIL, SSOIL, LIMS)

def gen_lum_meas(normal):
    return gen_complete_vector(normal,MLUM, SLUM, LIML)

    
def gen_complete(normal=[0,0,0,0]):
    
    if len(normal)!=4:
        print("error normal should have len 3")
        exit()
    
    t = gen_temp_meas(normal[0])
    
    h = gen_hum_meas(normal[1])

    s = gen_soil_meas(normal[2])
    
    l = gen_lum_meas(normal[3])
    
    return t,h,s,l