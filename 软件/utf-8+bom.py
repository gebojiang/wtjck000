#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为当前文件夹及所有递归子文件夹中指定的UTF-8文件类型添加BOM.
支持的文件类型: .cu, .c, .cpp, .h, .txt, .md, .mk ,.cuh
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

def add_bom_to_file(file_path, dry_run=False, verbose=False):
    """为单个文件添加UTF-8 BOM"""
    try:
        # 检查是否已有BOM,有则跳过
        if has_utf8_bom(file_path):
            if verbose:
                print(f"跳过 {file_path} - 已有BOM")
            return True, "already_has_bom"
        
        # 检查是否为文本文件
        if not is_text_file(file_path):
            if verbose:
                print(f"跳过 {file_path} - 可能不是文本文件")
            return True, "not_text_file"
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if dry_run:
            if verbose:
                print(f"[干运行] 将为 {file_path} 添加BOM")
            return True, "dry_run"
        
        # 写入带BOM的内容
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        
        if verbose:
            print(f"✓ 成功为 {file_path} 添加BOM")
        
        return True, "bom_added"
        
    except UnicodeDecodeError:
        if verbose:
            print(f"✗ 解码失败 {file_path} - 可能不是UTF-8编码")
        return False, "not_utf8"
    except Exception as e:
        if verbose:
            print(f"✗ 处理失败 {file_path}: {str(e)}")
        return False, f"error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='为指定文件类型添加UTF-8 BOM')
    parser.add_argument('--dry-run', action='store_true', 
                       help='干运行模式,不实际修改文件')
    parser.add_argument('--verbose', action='store_true', 
                       help='显示详细信息')
    parser.add_argument('--extensions', nargs='+', 
                       default=['cu', 'c', 'cpp', 'h', 'txt', 'md', 'mk','cuh'],
                       help='要处理的文件扩展名(默认: cu c cpp h txt md mk)')
    parser.add_argument('--exclude-dirs', nargs='+',
                       default=['.git', '__pycache__', 'node_modules', 'venv'],
                       help='要排除的目录名')
    
    args = parser.parse_args()
    
    # 获取当前目录
    current_dir = Path.cwd()
    
    print(f"扫描目录: {current_dir}")
    print(f"文件类型: {', '.join(args.extensions)}")
    print(f"排除目录: {', '.join(args.exclude_dirs)}")
    
    if args.dry_run:
        print("*** 干运行模式 - 不会实际修改文件 ***")
    
    # 统计信息
    stats = {
        'total_found': 0,
        'bom_added': 0,
        'already_has_bom': 0,
        'not_text_file': 0,
        'not_utf8': 0,
        'errors': 0
    }
    
    # 遍历所有指定扩展名的文件
    for extension in args.extensions:
        pattern = f"**/*.{extension}"
        for file_path in current_dir.glob(pattern):
            # 跳过目录
            if file_path.is_dir():
                continue
                
            # 检查是否在排除目录中
            if any(exclude_dir in file_path.parts for exclude_dir in args.exclude_dirs):
                continue
            
            stats['total_found'] += 1
            
            # 添加BOM
            success, result = add_bom_to_file(
                file_path, 
                dry_run=args.dry_run, 
                verbose=args.verbose
            )
            
            # 更新统计
            if result == "bom_added":
                stats['bom_added'] += 1
            elif result == "already_has_bom":
                stats['already_has_bom'] += 1
            elif result == "not_text_file":
                stats['not_text_file'] += 1
            elif result.startswith("not_utf8"):
                stats['not_utf8'] += 1
            elif result.startswith("error"):
                stats['errors'] += 1
    
    # 输出统计信息
    print("\n" + "="*50)
    print("添加BOM完成!统计信息:")
    print(f"扫描的文件总数: {stats['total_found']}")
    print(f"成功添加BOM: {stats['bom_added']}")
    print(f"已有BOM: {stats['already_has_bom']}")
    print(f"非文本文件: {stats['not_text_file']}")
    print(f"非UTF-8编码: {stats['not_utf8']}")
    print(f"错误: {stats['errors']}")
    
    if args.dry_run:
        print(f"\n干运行模式:如果实际执行,将为 {stats['bom_added']} 个文件添加BOM")

if __name__ == "__main__":
    main()