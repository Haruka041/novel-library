"""
标签初始化脚本
创建预定义的系统标签
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Tag


async def init_tags():
    """初始化预定义标签"""
    
    # 预定义标签
    predefined_tags = [
        # 年龄分级标签
        {"name": "全年龄", "type": "age_rating", "description": "适合所有年龄段阅读"},
        {"name": "12+", "type": "age_rating", "description": "适合12岁及以上读者"},
        {"name": "16+", "type": "age_rating", "description": "适合16岁及以上读者"},
        {"name": "18+", "type": "age_rating", "description": "仅限成人阅读"},
        
        # 题材标签
        {"name": "科幻", "type": "genre", "description": "科幻类小说"},
        {"name": "奇幻", "type": "genre", "description": "奇幻类小说"},
        {"name": "推理", "type": "genre", "description": "推理、侦探类小说"},
        {"name": "悬疑", "type": "genre", "description": "悬疑类小说"},
        {"name": "恐怖", "type": "genre", "description": "恐怖、惊悚类小说"},
        {"name": "言情", "type": "genre", "description": "言情、爱情类小说"},
        {"name": "武侠", "type": "genre", "description": "武侠类小说"},
        {"name": "仙侠", "type": "genre", "description": "仙侠、修真类小说"},
        {"name": "玄幻", "type": "genre", "description": "玄幻类小说"},
        {"name": "历史", "type": "genre", "description": "历史类小说"},
        {"name": "军事", "type": "genre", "description": "军事类小说"},
        {"name": "游戏", "type": "genre", "description": "游戏类小说"},
        {"name": "竞技", "type": "genre", "description": "竞技类小说"},
        {"name": "灵异", "type": "genre", "description": "灵异类小说"},
        {"name": "同人", "type": "genre", "description": "同人作品"},
        {"name": "轻小说", "type": "genre", "description": "轻小说"},
        
        # 内容警告标签
        {"name": "暴力", "type": "custom", "description": "包含暴力内容"},
        {"name": "血腥", "type": "custom", "description": "包含血腥描写"},
        {"name": "情色", "type": "custom", "description": "包含情色内容"},
        {"name": "脏话", "type": "custom", "description": "包含粗俗语言"},
        {"name": "药物", "type": "custom", "description": "涉及药物使用"},
        {"name": "恐怖元素", "type": "custom", "description": "包含恐怖元素"},
        
        # 其他常用标签
        {"name": "完结", "type": "custom", "description": "已完结作品"},
        {"name": "连载", "type": "custom", "description": "连载中作品"},
        {"name": "短篇", "type": "custom", "description": "短篇小说"},
        {"name": "长篇", "type": "custom", "description": "长篇小说"},
        {"name": "经典", "type": "custom", "description": "经典作品"},
        {"name": "热门", "type": "custom", "description": "热门作品"},
    ]
    
    async with AsyncSessionLocal() as session:
        created_count = 0
        skipped_count = 0
        
        for tag_data in predefined_tags:
            # 检查标签是否已存在
            result = await session.execute(
                select(Tag).where(Tag.name == tag_data["name"])
            )
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                print(f"⏭️  标签已存在：{tag_data['name']}")
                skipped_count += 1
                continue
            
            # 创建新标签
            tag = Tag(**tag_data)
            session.add(tag)
            created_count += 1
            print(f"✅ 创建标签：{tag_data['name']} ({tag_data['type']})")
        
        # 提交事务
        await session.commit()
        
        print(f"\n📊 初始化完成！")
        print(f"   - 新创建: {created_count} 个标签")
        print(f"   - 已存在: {skipped_count} 个标签")
        print(f"   - 总计: {len(predefined_tags)} 个预定义标签")


if __name__ == "__main__":
    print("🏷️  开始初始化预定义标签...")
    asyncio.run(init_tags())
