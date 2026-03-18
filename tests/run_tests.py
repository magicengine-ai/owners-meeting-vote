#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本
用法：
    python run_tests.py              # 运行所有测试
    python run_tests.py --cov        # 运行测试并生成覆盖率报告
    python run_tests.py --module auth  # 运行指定模块测试
    python run_tests.py --html       # 生成 HTML 测试报告
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime


def run_tests(module=None, coverage=False, html_report=False, verbose=False):
    """运行测试"""
    
    # 构建 pytest 命令
    cmd = [sys.executable, "-m", "pytest"]
    
    # 添加详细输出
    if verbose:
        cmd.append("-v")
    
    # 添加覆盖率
    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])
    
    # 添加 HTML 报告
    if html_report:
        cmd.extend([
            "--html=report/test_report.html",
            "--self-contained-html"
        ])
    
    # 添加 JUnit XML 报告（用于 CI/CD）
    cmd.extend([
        "--junitxml=report/junit.xml"
    ])
    
    # 指定测试模块
    if module:
        test_file = f"tests/test_{module}.py"
        if os.path.exists(test_file):
            cmd.append(test_file)
        else:
            print(f"❌ 测试文件不存在：{test_file}")
            return False
    else:
        cmd.append("tests/")
    
    # 打印命令
    print(f"\n🔧 运行测试命令：{' '.join(cmd)}\n")
    print("=" * 60)
    
    # 运行测试
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(__file__)))
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ 未找到 pytest，请先安装：pip install pytest pytest-cov pytest-html")
        return False
    except Exception as e:
        print(f"❌ 运行测试失败：{e}")
        return False


def print_summary(success):
    """打印测试总结"""
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试全部通过！")
    else:
        print("❌ 部分测试失败，请查看上面的错误信息")
    
    if os.path.exists("report/htmlcov/index.html"):
        print(f"\n📊 覆盖率报告：file://{os.path.abspath('report/htmlcov/index.html')}")
    
    if os.path.exists("report/test_report.html"):
        print(f"📄 HTML 报告：file://{os.path.abspath('report/test_report.html')}")
    
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="运行项目测试")
    parser.add_argument(
        "--module", "-m",
        type=str,
        choices=["auth", "vote", "meeting", "admin", "push"],
        help="运行指定模块的测试"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="生成测试覆盖率报告"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="生成 HTML 测试报告"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 创建报告目录
    os.makedirs("report", exist_ok=True)
    
    # 运行测试
    print(f"\n🚀 开始运行测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 测试目录：{os.path.abspath('tests')}")
    
    if args.module:
        print(f"🎯 测试模块：{args.module}")
    
    success = run_tests(
        module=args.module,
        coverage=args.coverage,
        html_report=args.html,
        verbose=args.verbose
    )
    
    # 打印总结
    print_summary(success)
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
