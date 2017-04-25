# -*- coding: utf-8 -*-

import re
import tree_clustering as tree
import numpy as np

# binary features for the toy credit dataset
credit_features = ['Buy-Car', 'Buy-House', 'Buy-Trip']

# binary features for the berkeley dataset
berkeley_features = ['A', 'B', 'C', 'D', 'E', 'F']

#
# Split a predicate 'feature <= threshold' into ['feature','<=','threshold']
# Remove feature group if present, and round thresholds
#
# @args p   predicate to be parsed
#
def parse_predicate(p):
    temp = re.split('( <= | > )',p)
    
    if '_' in temp[0]:
        temp[0] = temp[0].split('_')[1]
    
    temp[1] = temp[1].strip()
    
    temp[2] = str(int(float(temp[2])))
    
    return temp

#
# Header for the clustering table
#
# @args features the list of features, or (feature, threshold) tuples
# @args name     the name for the group of features
# @args vert     if true, display features vertically
#
def header_cluster(features, name, vert=False):
    h = ''
    h += '\\begin{tabular}{@{} l' + 'c'*len(features) + ' cc @{}}\n'
    h += '& \multicolumn{'+str(len(features))+'}{c}{'+name+'}\\\\'
    if vert:
        h += '[2ex]'
    h += '\n'
    if not vert:
        h += '\cline{2-'+str(len(features)+1)+'}\n'
    
    array = np.empty(len(features)+3, dtype=np.object)
    
    array[0] = ' '
    
    # rotate all features
    if vert:    
        features = map(lambda f: '\\rot{'+f[0]+' $>'+f[1]+'$}', features)
    
    array[1:len(features)+1] = features
    array[-2] = 'p-value'
    array[-1] = 'adj.\ p-value'
    
    h += ' & '.join(array) + ' \\\\ \n'
    h += '\\toprule\n'
    return h

#
# Header for the bias table
#
# @args sens     names of the two sensitive attributes
# @args users    name of the algorithm users
# @args target   name of the algorithm target
#    
def header_bias(sens, users, target):
    assert(len(sens) == 2)

    h = ''
    h += '\\begin{tabular}{@{} l  rr c rr @{}} \n'
    h += '& \multicolumn{2}{c}{'+sens[0]+'} '
    h += '&& \multicolumn{2}{c}{'+sens[1]+'} \\\\ \n'
    h += '\cline{2-3} \cline{5-6} \n'
    h += '& '+users+' & '+target+' && '+users+' & '+target+'\\\\ \n'
    h += '\\toprule\n'
    return h

#
# Format a p-value for output, in bold if significant
#
# @args num  number to format
# @args sig  whether the value is significant or not
#    
def format_pval(num, sig=False):
    f_num = ''
    
    # choose between floating point or scientific representation
    if num >= 0.01 or num == 0:
        f_num= '{:.2f}'.format(num)
    else:
        temp = '{:.2e}'.format(num)
        temp = temp.split('e-')
        temp = temp[0] + '\cdot 10^{-' + temp[1] + '}'
        f_num = temp
    
    f_num = '$'+f_num+'$'
    
    # bold significant values
    if sig:
        f_num = '\\boldmath'+f_num
    return f_num

#
# Format an integer for output, with thousand separators
#
# @args num  number to be formatted
#   
def format_int(num):
    temp = '${0:,}$'.format(num)
    temp = temp.replace(',', '{,}')
    return temp

#
# Format a percentage for output, in bold if significant
#
# @args num  number to be formatted
# @args sig  whether the value is significant or not
#       
def format_perc(num, sig=False):
    temp = '${:.2f}\%$'.format(num)
    
    if sig:
        temp = '\\boldmath'+temp
    return temp

#
# Output the latex table for the clusters
#
# @args clusters         the list of clusters
# @args features         the list of features. If None, features are collected
# @args features_name    the name to give the feature group in the header
# @args infer            if true, infer one of the features if all others are absent
# @args vert             if true, features are displayed vertically in the header
# @args sig              significance level for p-values
#
def print_cluster_tab(clusters, features, features_name, infer=True, vert=False, sig=0.05):
    res = ''
    
    # find all used features
    if features == None:
        features = collect_features(clusters)
    
    # format header
    res += header_cluster(features, features_name, vert)
    
    leaf_idx = 0
    array = np.empty((len(clusters), len(features)+3), dtype=np.object)
    
    for (idx,clst) in enumerate(clusters):
        if clst.ctype is tree.C_ROOT:
            # the root has no features
            array[idx,0] = 'ROOT'
            array[idx,1:len(features)+1] = ['-']*len(features)  
        elif clst.ctype is tree.C_LEAF:
            leaf_idx += 1
            array[idx,0] = ('LEAF '+str(leaf_idx))
            
            # temporary tables for inference of features
            temp_full = ['\OK']*len(features)
            temp_none = ['-']*len(features)
            
            # parse all predicates of this clusters
            clst_f = map(parse_predicate, clst.path)
            
            found = False
            for idx_f,f in enumerate(features):
                for pred in  clst_f:
                    if not infer:
                        # check if a feature, threshold pair matches
                        if f[0] == pred[0] and f[1] == pred[2]:
                            found = True
                            
                            # check if the predicate is satisfied or not
                            if pred[1] == '>':
                                temp_none[idx_f] = '\OK'
                            else:
                                temp_none[idx_f] = '\NOK'
                    else:
                        # in the inference case, we consider only binary 
                        # features. If all tested features are false, we infer 
                        # that the remaining one is true
                        if f == pred[0]:
                            if pred[1] == '>':
                                temp_none[idx_f] = '\OK'
                                found = True
                            else:
                                temp_full[idx_f] = '-'
            
            if found:
                array[idx,1:len(features)+1] = temp_none
            else:
                # infer that the feature which we haven't seen is true
                array[idx,1:len(features)+1] = temp_full
        
        # format p-values
        array[idx,-2] = format(format_pval(clst.p, sig=(clst.p <= sig)))
        array[idx,-1] = format(format_pval(clst.adj_p, sig=(clst.adj_p <= sig)))     
    
    # tranform array into latex table
    res += ' \\\\ \n'.join(map(lambda row: ' & '.join(row), array))
    res += '\n'
    
    res += '\end{tabular}'
    return res


#
# Output the latex table for the cluster biases
#
# @args clusters         the list of clusters
# @args sens             the names of the two sensitive attributes
# @args name             the name to give the users
# @args target           the name to give the target
# @args sig              significance level for p-values
#    
def print_bias_tab(clusters, sens=['Male', 'Female'], name='Applicants', target='Credit', sig=0.05):
    assert(len(sens) == 2)
    
    res = ''
    
    # format header
    res += header_bias(sens, name, target)
    
    leaf_idx = 0
    idx = 0
    
    # count number of clusters with significant bias
    num_sig = len(filter(lambda c: c.adj_p <= sig, clusters))
    array = np.empty((num_sig, 5), dtype=np.object)
    
    for clst in clusters:
        if clst.ctype is tree.C_LEAF:
            leaf_idx += 1
        
        # skip non.significant clusters    
        if (clst.adj_p > sig):
            continue
    
        if clst.ctype is tree.C_ROOT:
            array[idx,0] = 'ROOT'
        elif clst.ctype is tree.C_LEAF:
            array[idx,0] = ('LEAF '+str(leaf_idx))
         
        # compute size of sensitive groups    
        ct = clst.ct
        num_male = sum(ct[1])
        num_female = sum(ct[0])
        
        # compute target probabilities for both groups
        frac_male_yes = (100.0*ct[1][1])/num_male
        frac_female_yes = (100.0*ct[0][1])/num_female    
        
        array[idx,1] = format_int(num_male)
        array[idx,2] = format_perc(frac_male_yes, frac_male_yes>frac_female_yes)
        array[idx,3] = format_int(num_female)
        array[idx,4] = format_perc(frac_female_yes, frac_female_yes>frac_male_yes)
        
        idx += 1
    
    # tranform array into latex table
    res += ' \\\\ \n'.join(map(lambda row: ' & '.join(row[0:3]) + ' && ' + ' & '.join(row[3:5]), array))
    res += '\n'    
    res += '\end{tabular}'
    return res

#
# Find all features used to define the clusters
#
# @args clusters the list of clusters
#    
def collect_features(clusters):
    features = set()
    
    for clst in clusters:
        for f in clst.path:
            pred = parse_predicate(f)
            features.add((pred[0],pred[2]))
    
    return sorted(list(features))