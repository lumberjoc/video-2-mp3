import pika, json
'''
1) Upload file to mongoDB using gridFS
2) After successful upload put a message in queue
3) Downstream service pull message from queue
4) Process upload by pulling it from mongoDB
'''
def upload(f, fs, channel, access): # (file, gridFS instance, rabbitmq channel, user's acces)
    # Try to put a file into mongoDB and return a fileID if successful (fid)
    try:
        fid = fs.put(f) 
    except Exception as err:
        return "internal server erro, file did not upload", 500
    
    # After successful file upload, create a message for the queue
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video", # Name of the queue
            body=json.dumps(message), # Converts/Serializes python object into json string 
            properties=pika.BasicProperties(
                # Ensure messages persists in queue in event of pod crash or pod restart 
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except:
        fs.delete(fid)
        return "internal server error, File Deleted Not Converted", 500