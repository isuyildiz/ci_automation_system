from datetime import datetime

from pydantic import BaseModel, HttpUrl

from app.models.repository_member import RepoRole


class RepositoryCreate(BaseModel):
    url: HttpUrl
    default_branch: str = 'main'
    webhook_secret: str


class RepositoryResponse(BaseModel):
    id: str
    url: str
    default_branch: str
    created_at: datetime
    my_role: RepoRole

    model_config = {"from_attributes": True}
