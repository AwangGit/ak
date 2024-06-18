import os
import re
import subprocess
import sys
import importlib.metadata

# 定义目标目录和requirements文件路径
target_dir = "D:\\Project\\Shared_packages"
requirements_file = "requirements.txt"

# 读取requirements文件并获取包列表
with open(requirements_file, "r") as file:
    packages = [line.strip() for line in file if line.strip()]

# 获取目标目录中的现有文件
existing_files = os.listdir(target_dir)

# 函数：检查包是否存在于共享包目录中
def package_exists(package_name, file_list):
    normalized_package_name = package_name.replace('-', '_').lower()
    pattern = re.compile(rf'{re.escape(normalized_package_name)}(-\d+(\.\d+)*.*)?(\.whl|\.tar\.gz|\.zip)?', re.IGNORECASE)
    match_details = []
    for file in file_list:
        normalized_file_name = file.replace('-', '_').lower()
        match = pattern.match(normalized_file_name)
        if match:
            match_details.append((package_name, file, True))
            return True, match_details
        else:
            match_details.append((package_name, file, False))
    return False, match_details

# 检查.venv环境中的包是否存在
def venv_package_exists(package_name):
    normalized_package_name = package_name.replace('-', '_').lower()
    installed_packages = importlib.metadata.distributions()
    installed_package_names = [pkg.metadata['Name'].lower().replace('-', '_') for pkg in installed_packages]
    match_details = []
    pattern = re.compile(rf'{re.escape(normalized_package_name)}(-\d+(\.\d+)*.*)?', re.IGNORECASE)
    for installed_package in installed_package_names:
        match = pattern.match(installed_package)
        if match:
            match_details.append((package_name, installed_package, True))
            return True, match_details
        else:
            match_details.append((package_name, installed_package, False))
    return False, match_details

# 下载包并安装
def download_package(package_name, target_directory):
    result = subprocess.run([sys.executable, '-m', 'pip', 'download', package_name, '-d', target_directory])
    return result.returncode == 0

def install_package_from_directory(package_name, target_directory):
    result = subprocess.run([
        sys.executable, '-m', 'pip', 'install', '--no-index', '--find-links', target_directory, package_name])
    return result.returncode == 0

# 初始化结果列表和统计数据
sharedpackage_matching_results = []
sharedpackage_download_results = []
venv_matching_results = []
install_results = []
sharedpackage_match_details = []
venv_match_details = []

# 统计数据初始化
total_packages = len(packages)
sharedpackage_matches = 0
proposed_downloads = 0
actual_downloads = 0
venv_matches = 0
proposed_installs = 0
actual_installs = 0

# 检查包名匹配情况并安装包
for package in packages:
    sharedpackage_exists, match_details = package_exists(package, existing_files)
    sharedpackage_matching_results.append((package, sharedpackage_exists))
    sharedpackage_match_details.extend(match_details)
    if sharedpackage_exists:
        sharedpackage_matches += 1

    if not sharedpackage_exists:
        proposed_downloads += 1
        download_success = download_package(package, target_dir)
        sharedpackage_download_results.append((package, download_success))
        if download_success:
            actual_downloads += 1
            sharedpackage_exists, _ = package_exists(package, os.listdir(target_dir))
    else:
        sharedpackage_download_results.append((package, "无需下载"))

    if sharedpackage_exists:
        venv_exists, venv_match_detail = venv_package_exists(package)
        venv_matching_results.append((package, venv_exists))
        venv_match_details.extend(venv_match_detail)
        if venv_exists:
            venv_matches += 1
        if not venv_exists:
            proposed_installs += 1
            install_success = install_package_from_directory(package, target_dir)
            install_results.append((package, install_success))
            if install_success:
                actual_installs += 1
        else:
            install_results.append((package, "无需安装"))
    else:
        venv_matching_results.append((package, False))
        install_results.append((package, False))

print("\n统计信息:")
print(f"总共检查的包数量: {total_packages}")
print(f"共享包目录匹配数: {sharedpackage_matches} 需下载数: {proposed_downloads} 实际下载数: {actual_downloads}")
print(f".venv环境匹配数: {venv_matches} 需安装数: {proposed_installs} 实际安装数: {actual_installs}")

show_details = input("是否打印详细信息？输入Y打印，其他键结束流程: ")

if show_details.lower() == 'y':
    print("\n共享包目录匹配结论:")
    for package, result in sharedpackage_matching_results:
        print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

    print("\n下载结论:")
    for package, result in sharedpackage_download_results:
        print(f"包 '{package}' 下载结果: {'成功' if result == True else '无需下载' if result == '无需下载' else '失败'}")

    print("\n.venv环境匹配结论:")
    for package, result in venv_matching_results:
        print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

    print("\n安装结论:")
    for package, result in install_results:
        print(f"包 '{package}' 安装结果: {'成功' if result == True else '无需安装' if result == '无需安装' else '失败'}")

    show_match_details = input("是否打印匹配详细信息？输入Y打印，其他键结束流程: ")

    if show_match_details.lower() == 'y':
        print("\n共享包匹配明细:")
        for package_name, file, matched in sharedpackage_match_details:
            print(f"检查包是否存在: {package_name}，匹配{'成功' if matched else '失败'}: {file}")

        print("\n.venv匹配明细:")
        for package_name, installed_package, matched in venv_match_details:
            print(f"检查包是否存在: {package_name}，匹配{'成功' if matched else '失败'}: {installed_package}")
else:
    print("流程结束。")