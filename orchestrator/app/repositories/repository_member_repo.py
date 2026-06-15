from sqlalchemy import delete as sql_delete
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository_member import RepoRole, RepositoryMember
from app.models.user import User


class RepositoryMemberRepository:

    async def add(self, session: AsyncSession, repo_id: str, user_id: str, role: str) -> RepositoryMember:
        member = RepositoryMember(repo_id=repo_id, user_id=user_id, role=role)
        session.add(member)
        await session.flush()
        await session.refresh(member)
        return member

    async def get(self, session: AsyncSession, repo_id: str, user_id: str) -> RepositoryMember | None:
        result = await session.execute(
            select(RepositoryMember).where(
                RepositoryMember.repo_id == repo_id,
                RepositoryMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_repo(self, session: AsyncSession, repo_id: str) -> list[tuple[RepositoryMember, str]]:
        """Returns (member, username) tuples ordered by role (owners first), then created_at."""
        result = await session.execute(
            select(RepositoryMember, User.username)
            .join(User, User.id == RepositoryMember.user_id)
            .where(RepositoryMember.repo_id == repo_id)
            .order_by(RepositoryMember.role.desc(), RepositoryMember.created_at)
        )
        return [(m, u) for m, u in result.all()]

    async def list_repo_ids_for_user(self, session: AsyncSession, user_id: str) -> list[str]:
        result = await session.execute(
            select(RepositoryMember.repo_id).where(RepositoryMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def is_member(self, session: AsyncSession, repo_id: str, user_id: str) -> bool:
        return (await self.get(session, repo_id, user_id)) is not None

    async def is_owner(self, session: AsyncSession, repo_id: str, user_id: str) -> bool:
        member = await self.get(session, repo_id, user_id)
        return member is not None and member.role == RepoRole.owner.value

    async def count_owners(self, session: AsyncSession, repo_id: str) -> int:
        from sqlalchemy import func
        result = await session.execute(
            select(func.count())
            .select_from(RepositoryMember)
            .where(
                RepositoryMember.repo_id == repo_id,
                RepositoryMember.role == RepoRole.owner.value,
            )
        )
        return result.scalar_one()

    async def update_role(self, session: AsyncSession, repo_id: str, user_id: str, role: str) -> None:
        await session.execute(
            update(RepositoryMember)
            .where(RepositoryMember.repo_id == repo_id, RepositoryMember.user_id == user_id)
            .values(role=role)
        )
        await session.flush()

    async def remove(self, session: AsyncSession, repo_id: str, user_id: str) -> bool:
        result = await session.execute(
            sql_delete(RepositoryMember).where(
                RepositoryMember.repo_id == repo_id,
                RepositoryMember.user_id == user_id,
            )
        )
        await session.flush()
        return result.rowcount > 0
