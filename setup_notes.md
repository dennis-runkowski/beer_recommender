# Install redis search
* git clone --recursive https://github.com/RediSearch/RediSearch.git
* sudo make setup
* make build
* make run

# Redis Search python client
* pip install redisearch

* install redis - https://www.multimedia-pool.com/article/118-redis-5-0-5-installation-update-upgrade/

* to run locally stop redis-server
systemctl stop redis-server
cd build/RedisSearch
make build
make run

running as module 
sudo cp redisearch.so /etc/redis/



# Search Query

get thumbs up/down
@user_thumbs_up:{user_id}

https://oss.redis.com/redisearch/Query_Syntax/

Use @field_name:query to search in one field