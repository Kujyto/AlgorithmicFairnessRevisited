# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sklearn.metrics as metrics
import sklearn.tree as tree
from sklearn.tree._tree import TREE_LEAF
import fairness_measures as fm

# Cluster types
C_LEAF      = 1
C_ROOT      = 2
C_INTERNAL  = 3

#
# class for storing and analyzing a cluster
#
class Cluster:

    #
    # Constructor
    #
    # @args num              the cluster's number
    # @args path             the predicate path leading from the root to the cluster
    # @args ctype            the cluster type
    # @args data             the data contained in this cluster
    # @args sens             the name of the sensitive feature
    # @args out              the name of the algorithmic output feature
    def __init__(self, num, path, ctype, data, sens, out):
        self.num = num
        self.path = path
        self.ctype = ctype
        self.size = len(data)
        self.ct = pd.crosstab(data[out], data[sens])

    #
    # Analyze the cluster's contingency table
    #
    # @args correction   if true, Yate's correction for continuity is applied
    # @args exact        if true, an exact Fisher test is used
    #
    def analyse_ct(self, correction=False, exact=False):
        self.mi     = 0
        self.G      = 0
        self.p      = 0
        self.pp     = 0
        self.adj_p  = 0
        self.sp     = 0

        # 1-dimensional tables have a p-value of 0
        if 1 not in self.ct.shape:
            # compute the mutual information
            self.mi = fm.mutual_info(self.ct, norm=False)

            # compute the G-Test
            self.G, self.p, _, _ = fm.G_test(self.ct)

        # compute exact tests
        if (exact):
            # compute the (Monte-Carlo) permutation test
            self.pp = fm.permutation_test(self.ct)

            # compute Fisher's exact test
            _, self.p = fm.Fisher_test(self.ct)

        # compute statistical parity and slifts
        if (self.ct.shape == (2,2)):
            self.sp =  fm.statistical_parity(self.ct)
            self.slifts = fm.slifts(self.ct)

    def __str__(self):
         ctype = "LEAF" if (self.ctype == C_LEAF) else "ROOT" if (self.ctype == C_ROOT) else "INTERNAL"
         ret  = '{} node {} of size {}\n'.format(ctype, self.num, self.size)
         ret += '{}\n'.format(self.path)
         ret += 'G-Test = {} ; p-value = {} ; p-value adj = {} ; permut p-value = {} ; MI = {}\n'.format(self.G, self.p, self.adj_p, self.pp, self.mi)

         if (self.ct.shape == (2,2)):
            slift = max(self.slifts[0], 1/self.slifts[0])
            slift_d = abs(self.slifts[1])
            ret += 'SP = {} ; Slift = {} ; Slift_d = {}\n'.format(self.sp, slift, slift_d)

         ret += str(self.ct)
         return ret

#
# Traverse the tree and output clusters for each node
#
# @args tree             the decision tree
# @args data             the dataset
# @args feature_names    the names of the dataset features
# @args sens             the name of the sensitive feature
# @args out              the name of the algorithmic output feature
# @args business         the name of the business feature
#
def find_clusters(tree, data, feature_names, sens, out):
        child_left_array      = tree.children_left
        child_right_array     = tree.children_right
        threshold_array       = tree.threshold
        #features_array        = [feature_names[i] for i in tree.feature] # version originale
        features_array        = [feature_names[i] if i >= 0 else 'ERROR_CASE' for i in tree.feature] # modification Bidouille
        print 'DEBUG Bidouille: [%s]' % ', '.join(map(str, features_array)) # DEBUG

        # list of clusters
        clusters = [None]*tree.node_count

        #
        # Simple BFS to traverse the tree
        #
        # @node         the current node
        # @data_temp    the sub-dataset rooted at this node
        # @feature_path The predicate path from the root to this node
        #
        def bfs(node, data_temp, feature_path):
            #current node
            feature = features_array[node]
            threshold = threshold_array[node]

            #check node type
            ctype = C_ROOT if (node == 0) else C_LEAF if (child_left_array[node] == TREE_LEAF) else C_INTERNAL

            # build a cluster class and store it in the list
            clstr = Cluster(node, feature_path, ctype, data_temp, sens, out)
            clusters[node] = clstr

            if ctype is not C_LEAF:
                # recurse left, split data based on predicate and add predicate
                # to path
                data_left = data_temp[data_temp[feature] <= threshold]
                bfs(child_left_array[node], data_left,
                    feature_path + [feature + ' <= ' + str(threshold)])

                # recurse left, split data based on predicate and add predicate
                # to path
                data_right = data_temp[data_temp[feature] > threshold]
                bfs(child_right_array[node], data_right,
                    feature_path + [feature + ' > ' + str(threshold)])

        # start bfs from the root with the full dataset and an empty path
        bfs(0, data, [])
        return clusters
