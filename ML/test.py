from utils import generate_embeddings
vecs = generate_embeddings(["one", "two", "three" , "four"])
print(len(vecs), [len(v) for v in vecs])