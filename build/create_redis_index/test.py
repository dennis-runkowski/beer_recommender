from redisearch import Client, TextField, IndexDefinition, Query, AutoCompleter,  Suggestion

# Creating a client with a given index name
def redis_client(index_name, port=6379, password=False):
    """Get redis client

    Args:
        index_name (str): Redis index name
        port (int): Port for redis
        password (str): Redis password
    Returns:
        obj: redis client
    """
    client = Client(
        index_name=index_name,
        host='localhost',
        port=port,
        password=password
    )
    return client


client = redis_client('beer_index')
# IndexDefinition is avaliable for RediSearch 2.0+
# definition = IndexDefinition(prefix=['doc:', 'article:'])

# Creating the index definition and schema
# client.create_index((TextField("title", weight=5.0), TextField("body")), definition=definition)

# Indexing a document for RediSearch 2.0+
# client.redis.hset('doc:1',
#                 mapping={
#                     'title': 'RediSearch',
#                     'body': 'Redisearch impements a search engine on top of redis',
#                     'name': 'dennis'
#                 })
# client.redis.hset('doc:2',
#                 mapping={
#                     'title': 'Dennis Testing',
#                     'body': 'Redisearch impements a search engine on top of redis'
#                 })


# the result has the total number of results, and a list of documents
# print(res.total) # "2"
# print(res.docs[0].title) # "RediSearch"

# Searching with complex parameters:
q = Query("*").paging(0, 100000)
res = client.search('@title:"Dennis Creek"')
titles = []
for i in res.docs:
    print(i.title)

