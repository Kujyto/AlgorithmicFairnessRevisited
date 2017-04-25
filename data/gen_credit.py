outfile = "credit.data"

buy_car = [[1500, 500],[500, 500]]
buy_house = [[500, 1500],[1500,1500]]
buy_trip = [[1000,1000], [1000,1000]]

purposes = {}
purposes["Buy-Car"]=buy_car
purposes["Buy-House"]=buy_house
purposes["Buy-Trip"]=buy_trip

Gender = ["Male", "Female"]
Credit = ["Yes", "No"]

with open(outfile, 'w+') as outf:
    for purpose in purposes.keys():
        tab = purposes[purpose]
        
        for i in range(0, 2):
            GENDER = Gender[i]
            
            for j in range(0, 2):
                CREDIT = Credit[j]
                
                for k in range(0, tab[i][j]):
                    outf.write(GENDER + ", " + purpose + ", " + CREDIT + "\n")
        
        