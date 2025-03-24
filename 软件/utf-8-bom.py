#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
移除当前文件夹及所有递归子文件夹中有UTF-8 BOM的文件中的BOM
支持所有文件类型,但只处理有BOM的文件
"""

import os
import sys
import codecs
import argparse
from pathlib import Path

def has_utf8_bom(file_path):
    """检查文件是否已经有UTF-8 BOM"""
    try:
        with open(file_path, 'rb') as f:
            bom = f.read(3)
            return bom == codecs.BOM_UTF8
    except Exception:
        return False

def is_text_file(file_path):
    """检查文件是否为文本文件"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            # 检查是否包含null字节（二进制文件标志）
            if b'\0' in chunk:
                return False
        return True
    except Exception:
        return False

def remove_bom_from_file(file_path, dry_run=False, verbose=False):
    """从单个文件中移除UTF-8 BOM"""
    try:
        # 检查是否有BOM，没有则跳过
        if not has_utf8_bom(file_path):
            if verbose:
                print(f"跳过 {file_path} - 无BOM")
            return True, "no_bom"
        
        # 检查是否为文本文件
        if not is_text_file(file_path):
            if verbose:
                print(f"跳过 {file_path} - 可能不是文本文件")
            return True, "not_text_file"
        
        # 读取文件内容（自动跳过BOM）
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        if dry_run:
            if verbose:
                print(f"[干运行] 将从 {file_path} 移除BOM")
            return True, "dry_run"
        
        # 写入无BOM的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if verbose:
            print(f"✓ 成功从 {file_path} 移除BOM")
        
        return True, "bom_removed"
        
    except UnicodeDecodeError:
        if verbose:
            print(f"✗ 解码失败 {file_path} - 可能不是UTF-8编码")
        return False, "not_utf8"
    except Exception as e:
        if verbose:
            print(f"✗ 处理失败 {file_path}: {str(e)}")
        return False, f"error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='移除所有有UTF-8 BOM的文件中的BOM')
    parser.add_argument('--dry-run', action='store_true', 
                       help='干运行模式,不实际修改文件')
    parser.add_argument('--verbose', action='store_true', 
                       help='显示详细信息')
    parser.add_argument('--exclude-dirs', nargs='+',
                       default=['.git', '__pycache__', 'node_modules', 'venv'],
                       help='要排除的目录名')
    parser.add_argument('--extensions', nargs='+',
                       help='只处理指定扩展名的文件 (默认：所有文件)')
    
    args = parser.parse_args()
    
    # 获取当前目录
    current_dir = Path.cwd()
    
    print(f"扫描目录: {current_dir}")
    print(f"排除目录: {', '.join(args.exclude_dirs)}")
    if args.extensions:
        print(f"文件类型: {', '.join(args.extensions)}")
    else:
        print("文件类型: 所有文件")
    
    if args.dry_run:
        print("*** 干运行模式 - 不会实际修改文件 ***")
    
    # 统计信息
    stats = {
        'total_checked': 0,
        'bom_removed': 0,
        'no_bom': 0,
        'not_text_file': 0,
        'not_utf8': 0,
        'errors': 0
    }
    
    # 遍历所有文件
    if args.extensions:
        # 只处理指定扩展名的文件
        patterns = [f"**/*.{ext}" for ext in args.extensions]
    else:
        # 处理所有文件
        patterns = ["**/*"]
    
    for pattern in patterns:
        for file_path in current_dir.glob(pattern):
            # 跳过目录
            if file_path.is_dir():
                continue
                
            # 检查是否在排除目录中
            if any(exclude_dir in file_path.parts for exclude_dir in args.exclude_dirs):
                continue
            
            stats['total_checked'] += 1
            
            # 移除BOM
            success, result = remove_bom_from_file(
                file_path, 
                dry_run=args.dry_run, 
                verbose=args.verbose
            )
            
            # 更新统计
            if result == "bom_removed":
                stats['bom_removed'] += 1
            elif result == "no_bom":
                stats['no_bom'] += 1
            elif result == "not_text_file":
                stats['not_text_file'] += 1
            elif result.startswith("not_utf8"):
                stats['not_utf8'] += 1
            elif result.startswith("error"):
                stats['errors'] += 1
    
    # 输出统计信息
    print("\n" + "="*50)
    print("移除BOM完成!统计信息:")
    print(f"扫描的文件总数: {stats['total_checked']}")
    print(f"成功移除BOM: {stats['bom_removed']}")
    print(f"无BOM: {stats['no_bom']}")
    print(f"非文本文件: {stats['not_text_file']}")
    print(f"非UTF-8编码: {stats['not_utf8']}")
    print(f"错误: {stats['errors']}")
    
    if args.dry_run:
        print(f"\n干运行模式: 如果实际执行,将从 {stats['bom_removed']} 个文件移除BOM")

if __name__ == "__main__":
    main()