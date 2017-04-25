import numpy as np

outfile = "berkeley.data"

# admissions data
A = [[512, 313], [89, 19]]
B = [[353, 207], [17, 8]]
C = [[120, 205], [202, 391]]
D = [[138, 279], [131, 244]]
E = [[53, 138], [94, 299]]
F = [[16, 256], [24, 317]]

depts = {}
depts["A"]=A
depts["B"]=B
depts["C"]=C
depts["D"]=D
depts["E"]=E
depts["F"]=F

Gender = ["Male", "Female"]
Admitted = ["Yes", "No"]

with open(outfile, 'w+') as outf:
    for dept in sorted(depts.keys()):
        tab = depts[dept]
        
        p_male = (100.0*tab[0][0])/sum(tab[0])
        p_female = (100.0*tab[1][0])/sum(tab[1])
        print '{}: {:.0f}% - {:.0f}%'.format(dept, round(p_male), round(p_female))
        
        for i in range(0, 2):
            GENDER = Gender[i]
            
            for j in range(0, 2):
                ADMIT = Admitted[j]
                
                for k in range(0, tab[i][j]):
                    outf.write(GENDER + ", " + dept + ", " + ADMIT + "\n")
        

data = np.array(depts.values())
data = data.sum(axis=0)
p_male = (100.0*data[0][0])/sum(data[0])
p_female = (100.0*data[1][0])/sum(data[1])
print 'tot: {:.2f}% - {:.2f}%'.format((p_male), (p_female))