from utils_dict_xml import *

#pack variables into a dictionary
params_dict_root={'root':{
                    'SCUCa':SCUCa,
                    'SCUCb':SCUCb,
                    'SCUCc':SCUCc,
                    'SCUCalpha':SCUCalpha,                   
                    'SCUCbeta':SCUCbeta,                                          
                    'SCUCgamma':SCUCgamma,                
                    'SCCOux':SCCOux,
                    'SCCOuy':SCCOuy,                        
                    'SCCOuz':SCCOuz,            
                    'SCCOvx':SCCOvx,
                    'SCCOvy':SCCOvy,                        
                    'SCCOvz':SCCOvz,     
                    'SCGSPsi':SCCOPsi,                        
                    'SCGSMN':SCCOMN,                        
                    'SCVAu1a':SCVAu1a,                    
                    'SCVAu1b':SCVAu1b,                        
                    'SCVAu1c':SCVAu1c,                        
                    'SCVAu1Label':SCVAu1Label,
                    'SCVAu2a':SCVAu2a,                       
                    'SCVAu2b':SCVAu2b,                        
                    'SCVAu2c':SCVAu2c,                        
                    'SCVAu2Label':SCVAu2Label,                        
                    'SCVAu3a':SCVAu3a,
                    'SCVAu3b':SCVAu3b,                        
                    'SCVAu3c':SCVAu3c,                        
                    'SCVAu3Label':SCVAu3Label                                                
                }}
                
#view key:value pairs for debug
params_dict=params_dict_root.get('root') 
for key,value in params_dict.items():
    print "key: ",key,"  value: ",value, " type(value): ",type(value)
                
#create xml from dictionary and save xml to file
dicttoxmlfile(params_dict_root, filename)