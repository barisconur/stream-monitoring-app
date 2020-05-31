import pymongo
class MongoService:
    MONGO_CLIENT_URL = "mongodb+srv://admin:ascendant@cluster0-62hqm.mongodb.net/test?retryWrites=true&w=majority",
    MONGO_CLIENT = pymongo.MongoClient(MONGO_CLIENT_URL)
    DB_NAME = "VideoProxyDB"
    DB_COLLECTIONS = ["Video Chunks", "Streams"]

    @staticmethod
    def initDbAndCollections():
        MONGO_CLIENT_URL = "mongodb+srv://admin:ascendant@cluster0-62hqm.mongodb.net/test?retryWrites=true&w=majority"
        MONGO_CLIENT = pymongo.MongoClient(MONGO_CLIENT_URL)
        DB_NAME = "VideoProxyDB"
        DB_COLLECTIONS = ["Video Chunks", "Streams"]

        db_list = MONGO_CLIENT.list_database_names()
        if (DB_NAME in db_list):
            return

        db = MONGO_CLIENT[DB_NAME]
        video_chunks_collection = db[DB_COLLECTIONS[0]]
        videos_collection = db[DB_COLLECTIONS[1]]
        init_doc = {"name": "initObj"}

        video_chunks_collection.insert_one(init_doc)
        video_chunks_collection.delete_one(init_doc)
        videos_collection.insert_one(init_doc)
        videos_collection.delete_one(init_doc)

    @staticmethod
    def isVideoObjectIsCreated(id):
        db = MongoService.MONGO_CLIENT[MongoService.DB_NAME]
        collection = db[MongoService.DB_COLLECTIONS[1]]
        obj = collection.find_one({"id": id})
        if (obj != None):
            return True
        return False

    @staticmethod
    def addVideoToStreamsCollection(instance):
        if (MongoService.isVideoObjectIsCreated(instance['id'])):
            return

        db = MongoService.MONGO_CLIENT[MongoService.DB_NAME]
        collection = db[MongoService.DB_COLLECTIONS[1]]
        collection.insert_one(instance)

    @staticmethod
    def incrementChunkCount(collection, query, chunk):
        if ('video' in chunk['type'] or 'Muxed' in chunk['type']):
            new_values = { "$inc" : {"video_chunk_count" : 1}}
        else:
            new_values = { "$inc" : {"audio_chunk_count" : 1}}
        collection.update_one(query, new_values)

    @staticmethod
    def modifyYoutubeVideo(chunk):
        db = MongoService.MONGO_CLIENT[MongoService.DB_NAME]
        streamCollection = db[MongoService.DB_COLLECTIONS[1]]

        query = {"id": chunk["id"]}
        bitrate = chunk['bitrate']
        size = chunk['content_length']
        res = chunk['resolution']
        request_time = chunk['request_time']

        MongoService.incrementChunkCount(streamCollection, query, chunk)

        prevStreamDocument = streamCollection.find_one(query)
        prev_video_chunk_count = prevStreamDocument['video_chunk_count']
        prev_audio_chunk_count = prevStreamDocument['audio_chunk_count']

        if (prev_video_chunk_count + prev_audio_chunk_count == 1): # when first packet comes whether audio or video
            first_req_query = { "$set": { "first_request_time": request_time}}
            streamCollection.update_one(query, first_req_query)

        prev_size = prevStreamDocument['download_size']
        new_content_size = prev_size + size

        if ('video' in chunk['type']): #new video chunk added to DB
            prev_average_bitrate = prevStreamDocument['average_video_bitrate']
            prev_chunk_count = prevStreamDocument['video_chunk_count']
            videoAverage = ((prev_average_bitrate * (prev_chunk_count - 1)) + bitrate) / (prev_chunk_count)
            new_values =  {"$set": { "average_video_bitrate": videoAverage,
                                     "download_size": new_content_size,
                                     "last_request_time": request_time
                                     }}
            add_res = {"$push" : {"video_resolutions": res}}
            streamCollection.update_one(query, new_values)
            streamCollection.update_one(query, add_res)

        else: # new audio chunk added to DB
            new_values = {"$set":
                              {"download_size": new_content_size,
                               "last_request_time": request_time
                               }}
            add_res = {"$push" : {"audio_resolutions": res}}
            streamCollection.update_one(query, new_values)
            streamCollection.update_one(query, add_res)

    @staticmethod
    def modifyUdemyVideo(chunk):
        db = MongoService.MONGO_CLIENT[MongoService.DB_NAME]
        streamCollection = db[MongoService.DB_COLLECTIONS[1]]
        query = {"id": chunk['id']}
        bandwidth = chunk['bandwidth']
        size = chunk['content_length']
        res_signiture = chunk['res_signiture']
        video_length = chunk['video_length']
        request_time = chunk['request_time']

        MongoService.incrementChunkCount(streamCollection, query, chunk)

        prevStreamDocument = streamCollection.find_one(query)
        prev_size = prevStreamDocument['download_size']
        prev_chunk_count = prevStreamDocument['video_chunk_count']
        prev_average_bandwidth = prevStreamDocument['average_bandwidth']

        if (prev_chunk_count == 1):
            first_req_query = { "$set": { "first_request_time": request_time}}
            streamCollection.update_one(query, first_req_query)

        new_content_size = prev_size + size
        bandwidthAverage = ((prev_average_bandwidth * (prev_chunk_count - 1)) + bandwidth) / (prev_chunk_count)
        new_values = {"$set":
                          {"average_bandwidth": bandwidthAverage,
                           "download_size": new_content_size,
                           "video_length": video_length,
                           "last_request_time": request_time
                           }
                      }
        add_res = {"$push": {"video_resolutions": res_signiture}}
        streamCollection.update_one(query, new_values)
        streamCollection.update_one(query, add_res)

    @staticmethod
    def addChunk(instance):
        db = MongoService.MONGO_CLIENT[MongoService.DB_NAME]
        chunks_col = db[MongoService.DB_COLLECTIONS[0]]
        chunks_col.insert_one(instance)
