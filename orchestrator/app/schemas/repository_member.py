from datetime import datetime

from pydantic import BaseModel

from app.models.repository_member import RepoRole


class RepositoryMemberAdd(BaseModel):
    username: str
    role: RepoRole = RepoRole.member


class RepositoryMemberRoleUpdate(BaseModel):
    role: RepoRole


class RepositoryMemberResponse(BaseModel):
    id: str
    user_id: str
    username: str
    role: RepoRole
    created_at: datetime

    model_config = {"from_attributes": True}
