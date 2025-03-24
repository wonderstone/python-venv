from pymilvus import Collection
from pymilvus import __version__
from pymilvus import connections, db
print(__version__)

if __name__ == '__main__':

    from pymilvus import MilvusClient

    lient = MilvusClient("milvus_demo.db")