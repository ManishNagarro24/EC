import json

def error_data_response(statusMessage,statusCode,data):
        return {"statusCode":statusCode,
                "statusMessage":Exception(statusMessage),
                "dataAttached":data
                }

def error_map(errorOccured, data=None):
    statusMessage = errorOccured
    statusMessage = str(statusMessage)
    return error_data_response(statusMessage, 500, data)
