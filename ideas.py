# get markle tree and 


from pymerkle import MerkleTree
from graphviz import Digraph

# Define the leaves
leaves = ['a', 'b']

# Create the Merkle tree
merkle_tree = MerkleTree(leaves)

# Get the root hash
root_hash = merkle_tree.root()

# Create a Digraph object for the tree
dot = Digraph()
dot.node('root', str(root_hash))

# Add the leaves to the tree
for leaf in leaves:
        dot.node(str(leaf), str(leaf))
            dot.edge(str(root_hash), str(leaf))

            # Save the SVG file
            dot.format = 'svg'
            dot.render('merkle_tree')
