
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import TeamSchema
from models import Team, User, FavouriteTeam
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

async def get_team_by_id(db: AsyncSession, team_id: int) -> Team | None:
    stmt = select(Team).where(Team.espn_id == team_id)
    result = await db.execute(stmt)

    return result.scalars().one_or_none()


async def save_team_to_db(db: AsyncSession, team: TeamSchema | None) -> Team:
    if team is None:
        raise HTTPException(status_code=404, detail="Team data not found")

    if team.espn_id is None:
        raise HTTPException(status_code=400, detail="Team ESPN id is required")

    data = team.model_dump(exclude={"id"})
    existing_team = await get_team_by_id(db, team.espn_id)

    if existing_team is not None:
        for key, value in data.items():
            setattr(existing_team, key, value)

        await db.commit()
        await db.refresh(existing_team)
        return existing_team

    new_team = Team(**data)
    db.add(new_team)
    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise
    await db.refresh(new_team)
    return new_team


async def add_favourite_team(db: AsyncSession, user: User, team: Team) -> FavouriteTeam:
    stmt = select(FavouriteTeam).where(FavouriteTeam.user_id == user.id, FavouriteTeam.team_id == team.id,)
    result = await db.execute(stmt)
    existing_fav = result.scalars().one_or_none()
    if existing_fav:
        raise HTTPException(status_code=409, detail="Team already favourited")
    
    fav_team = FavouriteTeam(user_id=user.id, team_id=team.id)
    db.add(fav_team)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Team already favourited")
    except SQLAlchemyError:
        await db.rollback()
        raise
   
    await db.refresh(fav_team)
    stmt = (
        select(FavouriteTeam)
        .options(selectinload(FavouriteTeam.team))
        .where(FavouriteTeam.id == fav_team.id)
    )

    result = await db.execute(stmt)

    return result.scalar_one()

async def delete_favourite_team(db: AsyncSession, user: User, team: Team):
    stmt = select(FavouriteTeam).where(FavouriteTeam.user_id == user.id, FavouriteTeam.team_id == team.id,)
    result = await db.execute(stmt)
    existing_fav = result.scalars().one_or_none()
    if not existing_fav:
        raise HTTPException(status_code=404, detail="Favourite team not found")
    
    await db.delete(existing_fav)
    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise
    

async def get_user_favourite_teams(db: AsyncSession, user: User) -> list[FavouriteTeam]:
    stmt = (
        select(FavouriteTeam)
        .options(selectinload(FavouriteTeam.team))
        .where(FavouriteTeam.user_id == user.id)
    )
    result = await db.execute(stmt)
    fav_teams = result.scalars().all()
    return fav_teams