"""
权限管理路由
处理用户书库访问权限的分配和管理
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Library, LibraryPermission, User
from app.web.routes.auth import get_current_admin, get_current_user
from app.utils.logger import log

router = APIRouter()


# ===== Pydantic 模型 =====

class PermissionCreate(BaseModel):
    """创建权限请求"""
    user_id: int
    library_id: int


class PermissionResponse(BaseModel):
    """权限响应"""
    id: int
    user_id: int
    library_id: int
    username: str
    library_name: str
    created_at: str
    
    class Config:
        from_attributes = True


class UserLibraryResponse(BaseModel):
    """用户书库响应"""
    id: int
    name: str
    path: str
    is_public: bool
    has_permission: bool  # 是否有权限（通过授权或公共）
    
    class Config:
        from_attributes = True


# ===== 权限管理 =====

@router.post("/permissions/library", response_model=PermissionResponse)
async def grant_library_access(
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    为用户授予书库访问权限（需要管理员权限）
    
    Args:
        permission_data: 权限数据
        db: 数据库会话
        admin: 当前管理员
        
    Returns:
        权限信息
    """
    # 检查用户是否存在
    user = await db.get(User, permission_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查书库是否存在
    library = await db.get(Library, permission_data.library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书库不存在"
        )
    
    # 检查是否已存在权限
    result = await db.execute(
        select(LibraryPermission)
        .where(LibraryPermission.user_id == permission_data.user_id)
        .where(LibraryPermission.library_id == permission_data.library_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已拥有此书库的访问权限"
        )
    
    # 创建权限
    permission = LibraryPermission(
        user_id=permission_data.user_id,
        library_id=permission_data.library_id
    )
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    
    log.info(f"管理员 {admin.username} 为用户 {user.username} 授予书库 {library.name} 的访问权限")
    
    return {
        "id": permission.id,
        "user_id": permission.user_id,
        "library_id": permission.library_id,
        "username": user.username,
        "library_name": library.name,
        "created_at": permission.created_at.isoformat()
    }


@router.delete("/permissions/library/{permission_id}")
async def revoke_library_access(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    撤销用户书库访问权限（需要管理员权限）
    
    Args:
        permission_id: 权限 ID
        db: 数据库会话
        admin: 当前管理员
        
    Returns:
        操作结果
    """
    permission = await db.get(LibraryPermission, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限记录不存在"
        )
    
    # 获取用户和书库信息用于日志
    user = await db.get(User, permission.user_id)
    library = await db.get(Library, permission.library_id)
    
    await db.delete(permission)
    await db.commit()
    
    log.info(f"管理员 {admin.username} 撤销了用户 {user.username if user else permission.user_id} 对书库 {library.name if library else permission.library_id} 的访问权限")
    
    return {"status": "success", "message": "权限已撤销"}


@router.delete("/permissions/user/{user_id}/library/{library_id}")
async def revoke_user_library_access(
    user_id: int,
    library_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    通过用户ID和书库ID撤销权限（需要管理员权限）
    
    Args:
        user_id: 用户 ID
        library_id: 书库 ID
        db: 数据库会话
        admin: 当前管理员
        
    Returns:
        操作结果
    """
    result = await db.execute(
        select(LibraryPermission)
        .where(LibraryPermission.user_id == user_id)
        .where(LibraryPermission.library_id == library_id)
    )
    permission = result.scalar_one_or_none()
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限记录不存在"
        )
    
    await db.delete(permission)
    await db.commit()
    
    log.info(f"管理员 {admin.username} 撤销了用户 {user_id} 对书库 {library_id} 的访问权限")
    
    return {"status": "success", "message": "权限已撤销"}


@router.get("/permissions/user/{user_id}/libraries", response_model=List[UserLibraryResponse])
async def get_user_libraries(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    获取用户的书库权限列表（需要管理员权限）
    
    Args:
        user_id: 用户 ID
        db: 数据库会话
        admin: 当前管理员
        
    Returns:
        书库列表及权限状态
    """
    # 检查用户是否存在
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取所有书库
    result = await db.execute(select(Library))
    all_libraries = result.scalars().all()
    
    # 获取用户的权限
    permission_result = await db.execute(
        select(LibraryPermission.library_id)
        .where(LibraryPermission.user_id == user_id)
    )
    permission_library_ids = {row[0] for row in permission_result.all()}
    
    # 构建响应
    response = []
    for library in all_libraries:
        has_permission = library.is_public or library.id in permission_library_ids
        response.append({
            "id": library.id,
            "name": library.name,
            "path": library.path,
            "is_public": library.is_public,
            "has_permission": has_permission
        })
    
    return response


@router.get("/permissions/library/{library_id}/users")
async def get_library_users(
    library_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    获取书库的用户权限列表（需要管理员权限）
    
    Args:
        library_id: 书库 ID
        db: 数据库会话
        admin: 当前管理员
        
    Returns:
        用户列表及权限信息
    """
    # 检查书库是否存在
    library = await db.get(Library, library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书库不存在"
        )
    
    # 获取所有拥有此书库权限的用户
    result = await db.execute(
        select(LibraryPermission, User)
        .join(User, LibraryPermission.user_id == User.id)
        .where(LibraryPermission.library_id == library_id)
    )
    permissions = result.all()
    
    response = []
    for permission, user in permissions:
        response.append({
            "permission_id": permission.id,
            "user_id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "created_at": permission.created_at.isoformat()
        })
    
    return {
        "library_id": library.id,
        "library_name": library.name,
        "is_public": library.is_public,
        "users": response
    }


@router.get("/my-libraries", response_model=List[UserLibraryResponse])
async def get_my_libraries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户可访问的书库列表
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        可访问的书库列表
    """
    # 管理员可以看到所有书库
    if current_user.is_admin:
        result = await db.execute(select(Library))
        all_libraries = result.scalars().all()
        return [
            {
                "id": lib.id,
                "name": lib.name,
                "path": lib.path,
                "is_public": lib.is_public,
                "has_permission": True
            }
            for lib in all_libraries
        ]
    
    # 获取用户的权限
    permission_result = await db.execute(
        select(LibraryPermission.library_id)
        .where(LibraryPermission.user_id == current_user.id)
    )
    permission_library_ids = {row[0] for row in permission_result.all()}
    
    # 获取公共书库和有权限的书库
    result = await db.execute(
        select(Library)
        .where(
            (Library.is_public == True) | (Library.id.in_(permission_library_ids))
        )
    )
    libraries = result.scalars().all()
    
    return [
        {
            "id": lib.id,
            "name": lib.name,
            "path": lib.path,
            "is_public": lib.is_public,
            "has_permission": True
        }
        for lib in libraries
    ]
