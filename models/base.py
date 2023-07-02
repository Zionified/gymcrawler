from pydantic import BaseModel

class MongoBaseModel(BaseModel):
    mongo_id: str | None = None
    
    def from_bson(cls, **kwargs):
        if "_id" in kwargs:
            kwargs["_id"] = str(kwargs["_id"])
        obj = cls(**kwargs)
        obj.mongo_id = kwargs["_id"]
        return obj
            
    
    def to_bson(self):
        return self.model_dump(exclude=["mongo_id"])
        