# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 16:43:19 2024

@author: Eduin Hernandez
"""

import argparse
import os.path as osp
import torch

from dataset.fb_wiki import FB_Wiki
from torch_geometric.nn import ComplEx, DistMult, RotatE, TransE

# Define the model map again for reference
model_map = {
    'transe': TransE,
    'complex': ComplEx,
    'distmult': DistMult,
    'rotate': RotatE,
}

if __name__ == '__main__':
    
    # Setup the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=model_map.keys(), type=str.lower, required=True)
    parser.add_argument('--dimension_size', default=50, type=int)
    args = parser.parse_args()
    
    # Define the device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Define the path to the dataset
    path = 'D://Dewen//ML//datasets//FB-Wiki//'
    node_mapping = path + 'mapping//node_mapping.csv'
    relationship_mapping = path + 'mapping//relationship_mapping.json'
    
    # Load the test data
    train_data = FB_Wiki(path, split='train', node_mapping = node_mapping, rel_mapping = relationship_mapping)[0].to(device)
    test_data = FB_Wiki(path, split='test', node_mapping = node_mapping, rel_mapping = relationship_mapping)[0].to(device)
    
    # Initialize the model with the same configuration as when it was trained
    model_arg_map = {'rotate': {'margin': 9.0}}
    
    model = model_map[args.model](
        num_nodes=train_data.num_nodes,
        num_relations=train_data.num_edge_types,
        hidden_channels=args.dimension_size,
        **model_arg_map.get(args.model, {}),
    ).to(device)
    
    # Load the model parameters
    model_path = osp.join('models', f'fb_wiki/{args.model}_{args.dimension_size}_model.pth')
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Define the test function
    @torch.no_grad()
    def test(data):
        model.eval()
        return model.test(
            head_index=data.edge_index[0],
            rel_type=data.edge_type,
            tail_index=data.edge_index[1],
            batch_size=20000,
            k=10,
        )
    
    # Define the test function
    @torch.no_grad()
    def test_at_1(data):
        model.eval()
        return model.test(
            head_index=data.edge_index[0],
            rel_type=data.edge_type,
            tail_index=data.edge_index[1],
            batch_size=20000,
            k=1,
        )
    
    print('\n\n')
    print('--- FB-Wiki ---')
    print('--- ' + args.model + ' - Embeddings: '+ str(args.dimension_size) + ' ---')
    # print('\nSamples Size: %d' % len(test_data.edge_type))
    
    # Run the test function
    rank, mrr, hits_at_10 = test(test_data)
    print(f'Test Mean Rank: {rank:.2f}, Test MRR: {mrr:.4f}, Test Hits@10: {hits_at_10:.4f}')
    
    # Run the test function
    _, _, hits_at_1 = test_at_1(test_data)
    print(f'Test Hits@1: {hits_at_1:.4f}')
    
    result_path = f'./results/fb_wiki/{args.model}_{args.dimension_size}.txt'
    with open(result_path, 'w') as file:
        file.write(f'Test Mean Rank: {rank:.2f}\n')
        file.write(f'Test MRR: {mrr:.4f}\n')
        file.write(f'Test Hits@10: {hits_at_10:.4f}\n')
        file.write(f'Test Hits@1: {hits_at_1:.4f}\n')