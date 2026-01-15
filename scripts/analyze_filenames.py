"""
文件名分析脚本
分析书库中的文件命名模式，生成统计报告和解析规则建议
"""
import argparse
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models import Library
from app.utils.filename_analyzer import (
    FilenameAnalyzer,
    analyze_library_filenames,
    generate_analysis_report,
)
from app.utils.logger import log
from sqlalchemy import select


async def analyze_all_libraries():
    """分析所有书库的文件名"""
    async for db in get_db():
        # 获取所有书库
        result = await db.execute(select(Library))
        libraries = result.scalars().all()
        
        if not libraries:
            print("没有找到任何书库")
            return
        
        print(f"找到 {len(libraries)} 个书库\n")
        
        all_reports = []
        
        for library in libraries:
            print(f"分析书库: {library.name}")
            print(f"路径: {library.path}")
            print("-" * 80)
            
            library_path = Path(library.path)
            if not library_path.exists():
                print(f"  警告: 路径不存在\n")
                continue
            
            # 分析文件名
            report = analyze_library_filenames(library_path)
            
            if report.get('error'):
                print(f"  错误: {report['error']}\n")
                continue
            
            # 打印摘要
            print(f"  总文件数: {report['total_files']}")
            print(f"  模式覆盖率: {report['coverage']}%")
            print(f"  检测到的模式: {len(report['patterns_detected'])}\n")
            
            # 打印每个模式
            for pattern in report['patterns_detected'][:5]:  # 只显示前5个
                print(f"    {pattern['pattern']}: {pattern['count']} ({pattern['percentage']}%)")
            
            print()
            
            all_reports.append({
                'library': library.name,
                'report': report
            })
        
        return all_reports


async def analyze_single_library(library_id: int, output_file: str = None):
    """分析单个书库"""
    async for db in get_db():
        # 获取书库
        result = await db.execute(select(Library).where(Library.id == library_id))
        library = result.scalar_one_or_none()
        
        if not library:
            print(f"错误: 找不到 ID 为 {library_id} 的书库")
            return
        
        print(f"分析书库: {library.name}")
        print(f"路径: {library.path}")
        print("=" * 80)
        
        library_path = Path(library.path)
        if not library_path.exists():
            print(f"错误: 路径不存在")
            return
        
        # 生成详细报告
        output_path = Path(output_file) if output_file else None
        report_text = generate_analysis_report(library_path, output_path)
        
        # 打印报告
        print(report_text)
        
        # 同时生成解析器代码建议
        report = analyze_library_filenames(library_path)
        if not report.get('error'):
            analyzer = FilenameAnalyzer()
            parser_code = analyzer.generate_parser_code(report['patterns_detected'])
            
            print("\n" + "=" * 80)
            print("建议的解析器代码:")
            print("=" * 80)
            print(parser_code)
            
            # 如果指定了输出文件，也保存代码
            if output_file:
                code_file = Path(output_file).with_suffix('.py')
                code_file.write_text(parser_code, encoding='utf-8')
                print(f"\n解析器代码已保存到: {code_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='分析书库中的文件命名模式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析所有书库
  python scripts/analyze_filenames.py --all
  
  # 分析特定书库并生成报告
  python scripts/analyze_filenames.py --library 1 --output report.txt
  
  # 分析指定目录
  python scripts/analyze_filenames.py --path /path/to/books
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='分析所有书库'
    )
    
    parser.add_argument(
        '--library',
        type=int,
        metavar='ID',
        help='分析指定 ID 的书库'
    )
    
    parser.add_argument(
        '--path',
        type=str,
        metavar='PATH',
        help='分析指定路径的目录'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='输出报告文件路径'
    )
    
    args = parser.parse_args()
    
    # 检查参数
    if not (args.all or args.library or args.path):
        parser.print_help()
        return
    
    # 执行分析
    if args.all:
        asyncio.run(analyze_all_libraries())
    
    elif args.library:
        asyncio.run(analyze_single_library(args.library, args.output))
    
    elif args.path:
        library_path = Path(args.path)
        if not library_path.exists():
            print(f"错误: 路径不存在: {args.path}")
            return
        
        output_path = Path(args.output) if args.output else None
        report_text = generate_analysis_report(library_path, output_path)
        print(report_text)
        
        # 生成解析器代码
        report = analyze_library_filenames(library_path)
        if not report.get('error'):
            analyzer = FilenameAnalyzer()
            parser_code = analyzer.generate_parser_code(report['patterns_detected'])
            
            print("\n" + "=" * 80)
            print("建议的解析器代码:")
            print("=" * 80)
            print(parser_code)


if __name__ == '__main__':
    main()
