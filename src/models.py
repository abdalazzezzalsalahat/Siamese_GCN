import torch
import torch.nn as nn
import torch.nn.functional as F
from layers import GraphConvolution
import numpy as np
import dgl
from dgl.nn.pytorch.conv import ChebConv
import scipy.sparse as ss

class GCN_single(nn.Module):
    def __init__(self, nfeat, nhid, nclass, dropout, gc2_weight=None):
        super(GCN_single, self).__init__()

        self.gc1 = GraphConvolution(nfeat, nhid)
        self.gc2 = GraphConvolution(nhid, 2, gc2_weight)
        self.gc3 = nn.Linear(2, 1)
        self.dropout = dropout

    def forward(self, x, adj):
        x = F.relu(self.gc1(x, adj))
        x = F.dropout(x, self.dropout, training=self.training)
        x = self.gc2(x, adj)
        
        x.unsqueeze_(0)
        pooling = nn.MaxPool2d((adj.shape[0],1))
        x = pooling(x)
        x = self.gc3(x)
        
        return x


class GCN_hinge(nn.Module):
    def __init__(self, nfeat, nhid, nclass, dropout, gc2_weight):
        super(GCN_hinge, self).__init__()

        self.gc1 = ChebConv(nfeat, nhid, 3)
        self.gc2 = GraphConvolution(nhid, 2, gc2_weight)
        self.dropout = dropout

    def forward(self, x, adj):
        adj_ss = ss.coo_matrix((adj), shape=(adj.shape[0],adj.shape[1]))
        adj = torch.Tensor(adj)
        g = dgl.DGLGraph()
        g.from_scipy_sparse_matrix(adj_ss)
        
        x = F.relu(self.gc1(g, x))
        x = F.dropout(x, self.dropout, training=self.training)
        x = self.gc2(x, adj)
        
        x.unsqueeze_(0)
        pooling = nn.MaxPool2d((adj.shape[0],1))
        x = pooling(x)
        
        return x
