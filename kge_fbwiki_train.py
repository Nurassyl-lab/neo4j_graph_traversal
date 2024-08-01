import argparse
import os.path as osp
import os

import torch
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter  # Import for TensorBoard

from dataset.fb_wiki import FB_Wiki
from torch_geometric.nn import ComplEx, DistMult, RotatE, TransE

# from nn.TransEpa import TransEpa

model_map = {
    'transe': TransE,
    'complex': ComplEx,
    'distmult': DistMult,
    'rotate': RotatE,
    # 'transepa': TransEpa,
}

parser = argparse.ArgumentParser()
parser.add_argument('--model', choices=model_map.keys(), type=str.lower, required=True)
parser.add_argument('--epoch_num', default=1001, type=int)
parser.add_argument('--dimension_size', default=50, type=int)
args = parser.parse_args()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
path = 'D://Dewen//ML//datasets//FB-Wiki//'
node_mapping = path + 'mapping//node_mapping.csv'
relationship_mapping = path + 'mapping//relationship_mapping.json'

train_data = FB_Wiki(path, split='train', node_mapping = node_mapping, rel_mapping = relationship_mapping)[0].to(device)
val_data = FB_Wiki(path, split='val', node_mapping = node_mapping, rel_mapping = relationship_mapping)[0].to(device)
test_data = FB_Wiki(path, split='test', node_mapping = node_mapping, rel_mapping = relationship_mapping)[0].to(device)

print(train_data.num_edge_types)
print(test_data.num_edge_types)

model_arg_map = {'rotate': {'margin': 9.0}}
model = model_map[args.model](
    num_nodes=train_data.num_nodes,
    num_relations=train_data.num_edge_types,
    hidden_channels=args.dimension_size,
    **model_arg_map.get(args.model, {}),
).to(device)

loader = model.loader(
    head_index=train_data.edge_index[0],
    rel_type=train_data.edge_type,
    tail_index=train_data.edge_index[1],
    batch_size=1000,
    shuffle=True,
)

optimizer_map = {
    'transe': optim.Adam(model.parameters(), lr=0.01),
    'complex': optim.Adagrad(model.parameters(), lr=0.001, weight_decay=1e-6),
    'distmult': optim.Adam(model.parameters(), lr=0.0001, weight_decay=1e-6),
    'rotate': optim.Adam(model.parameters(), lr=1e-3),
    'transepa': optim.Adam(model.parameters(), lr=0.01),
}

optimizer = optimizer_map[args.model]

# Initialize the TensorBoard writer
writer = SummaryWriter(log_dir=f'runs/fb_wiki/{args.model}_{args.dimension_size}')

def train(epoch):
    model.train()
    total_loss = total_examples = 0
    for head_index, rel_type, tail_index in loader:
        optimizer.zero_grad()
        loss = model.loss(head_index, rel_type, tail_index)
        loss.backward()
        optimizer.step()
        total_loss += float(loss) * head_index.numel()
        total_examples += head_index.numel()
    avg_loss = total_loss / total_examples
    writer.add_scalar('Loss/train', avg_loss, epoch)  # Log the loss to TensorBoard
    return avg_loss

@torch.no_grad()
def test(data, epoch, prefix='Val'):
    model.eval()
    rank, mrr, hits = model.test(
        head_index=data.edge_index[0],
        rel_type=data.edge_type,
        tail_index=data.edge_index[1],
        batch_size=20000,
        k=10,
    )
    writer.add_scalar(f'{prefix}/Mean Rank', rank, epoch)
    writer.add_scalar(f'{prefix}/MRR', mrr, epoch)
    writer.add_scalar(f'{prefix}/Hits@10', hits, epoch)
    return rank, mrr, hits

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

for epoch in range(1, args.epoch_num):
    loss = train(epoch)
    print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}')
    if epoch % 25 == 0:
        rank, mrr, hits = test(val_data, epoch)
        print(f'Epoch: {epoch:03d}, Val Mean Rank: {rank:.2f}, Val MRR: {mrr:.4f}, Val Hits@10: {hits:.4f}')

# Save the model
model_path = osp.join('models', f'fb_wiki/{args.model}2_{args.dimension_size}_model.pth')
os.makedirs('models', exist_ok=True)
torch.save(model.state_dict(), model_path)
print(f"Model saved to {model_path}")

rank, mrr, hits_at_10 = test(test_data, epoch=args.epoch_num, prefix='Test')
print(f'Test Mean Rank: {rank:.2f}, Test MRR: {mrr:.4f}, Test Hits@10: {hits_at_10:.4f}')

_, _, hits_at_1 = test_at_1(test_data)
print(f'Test Hits@1: {hits_at_1:.4f}')

result_path = f'./results/fb15k/{args.model}_{args.dimension_size}.txt'
with open(result_path, 'w') as file:
    file.write(f'Test Mean Rank: {rank:.2f}\n')
    file.write(f'Test MRR: {mrr:.4f}\n')
    file.write(f'Test Hits@10: {hits_at_10:.4f}\n')
    file.write(f'Test Hits@1: {hits_at_1:.4f}\n')

# Close the TensorBoard writer
writer.close()