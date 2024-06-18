import os  # 导入操作系统模块
import re  # 导入正则表达式模块
import subprocess  # 导入子进程模块，用于执行系统命令
import sys  # 导入系统模块
import importlib.metadata  # 导入importlib.metadata模块，用于检查已安装的包

# 定义目标目录和requirements文件路径
target_dir = "D:\\Project\\Shared_packages"  # 共享包目录
requirements_file = "requirements.txt"  # requirements文件路径

# 读取requirements文件并获取包列表
with open(requirements_file, "r") as file:  # 打开requirements文件
    packages = [line.strip() for line in file if line.strip()]  # 读取每行并去除空白行

# 获取目标目录中的现有文件
existing_files = os.listdir(target_dir)  # 获取目标目录中的文件列表

# 函数：检查包是否存在于共享包目录中
def package_exists(package_name, file_list):
    normalized_package_name = package_name.replace('-', '_').lower()  # 标准化包名
    # 正则表达式匹配包名，忽略版本号和文件扩展名，忽略大小写
    pattern = re.compile(rf'{re.escape(normalized_package_name)}(-\d+(\.\d+)*.*)?(\.whl|\.tar\.gz|\.zip)?', re.IGNORECASE)
    match_details = []  # 用于存储匹配过程的详细信息
    for file in file_list:  # 遍历文件列表
        normalized_file_name = file.replace('-', '_').lower()  # 标准化文件名
        match = pattern.match(normalized_file_name)  # 匹配文件名
        if match:  # 如果匹配成功
            match_details.append((package_name, file, True))  # 记录匹配成功的详细信息
            return True, match_details  # 返回True表示包存在，并返回详细信息
        else:
            match_details.append((package_name, file, False))  # 记录匹配失败的详细信息
    return False, match_details  # 如果所有文件都不匹配，返回False，并返回详细信息

# 检查.venv环境中的包是否存在
def venv_package_exists(package_name):
    normalized_package_name = package_name.replace('-', '_').lower()  # 标准化包名
    installed_packages = importlib.metadata.distributions()  # 获取已安装的包列表
    installed_package_names = [pkg.metadata['Name'].lower().replace('-', '_') for pkg in installed_packages]  # 标准化已安装的包名列表
    match_details = []  # 用于存储匹配过程的详细信息
    # 正则表达式匹配包名，忽略版本号和文件扩展名，忽略大小写
    pattern = re.compile(rf'{re.escape(normalized_package_name)}(-\d+(\.\d+)*.*)?', re.IGNORECASE)
    for installed_package in installed_package_names:  # 遍历已安装包名列表
        match = pattern.match(installed_package)  # 匹配包名
        if match:  # 如果匹配成功
            match_details.append((package_name, installed_package, True))  # 记录匹配成功的详细信息
            return True, match_details  # 返回True表示包存在，并返回详细信息
        else:
            match_details.append((package_name, installed_package, False))  # 记录匹配失败的详细信息
    return False, match_details  # 如果所有包都不匹配，返回False，并返回详细信息

# 下载包并安装
def download_package(package_name, target_directory):
    # 使用pip下载包到目标目录
    result = subprocess.run([sys.executable, '-m', 'pip', 'download', package_name, '-d', target_directory])
    return result.returncode == 0  # 返回下载结果，0表示成功

def install_package_from_directory(package_name, target_directory):
    # 使用pip从目标目录安装包
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--no-index', '--find-links', target_directory, package_name])
    return result.returncode == 0  # 返回安装结果，0表示成功

# 初始化结果列表和统计数据
sharedpackage_matching_results = []  # 共享包目录匹配结果
sharedpackage_download_results = []  # 下载结果
venv_matching_results = []  # 虚拟环境匹配结果
install_results = []  # 安装结果
sharedpackage_match_details = []  # 共享包匹配详细信息
venv_match_details = []  # 虚拟环境匹配详细信息

# 统计数据初始化
total_packages = len(packages)  # 总包数量
sharedpackage_matches = 0  # 共享包目录匹配数量
proposed_downloads = 0  # 拟处理的下载数量
actual_downloads = 0  # 实际下载数量
venv_matches = 0  # 虚拟环境匹配数量
proposed_installs = 0  # 拟处理的安装数量
actual_installs = 0  # 实际安装数量

# 检查包名匹配情况并安装包
for package in packages:
    sharedpackage_exists, match_details = package_exists(package, existing_files)  # 检查共享包目录中是否存在包
    sharedpackage_matching_results.append((package, sharedpackage_exists))  # 记录匹配结果
    sharedpackage_match_details.extend(match_details)  # 记录详细匹配信息
    if sharedpackage_exists:
        sharedpackage_matches += 1  # 增加共享包目录匹配数量

    if not sharedpackage_exists:  # 如果包不存在
        proposed_downloads += 1  # 增加拟处理的下载数量
        download_success = download_package(package, target_dir)  # 下载包
        sharedpackage_download_results.append((package, download_success))  # 记录下载结果
        if download_success:  # 如果下载成功
            actual_downloads += 1  # 增加实际下载数量
            sharedpackage_exists, _ = package_exists(package, os.listdir(target_dir))  # 重新检查共享包目录中是否存在包
    else:
        sharedpackage_download_results.append((package, "无需下载"))  # 如果包存在，记录无需下载

    if sharedpackage_exists:  # 如果包存在于共享包目录中
        venv_exists, venv_match_detail = venv_package_exists(package)  # 检查虚拟环境中是否存在包
        venv_matching_results.append((package, venv_exists))  # 记录虚拟环境匹配结果
        venv_match_details.extend(venv_match_detail)  # 记录详细匹配信息
        if venv_exists:
            venv_matches += 1  # 增加虚拟环境匹配数量
        if not venv_exists:  # 如果虚拟环境中不存在包
            proposed_installs += 1  # 增加拟处理的安装数量
            install_success = install_package_from_directory(package, target_dir)  # 安装包
            install_results.append((package, install_success))  # 记录安装结果
            if install_success:  # 如果安装成功
                actual_installs += 1  # 增加实际安装数量
        else:
            install_results.append((package, "无需安装"))  # 如果包存在于虚拟环境中，记录无需安装
    else:
        venv_matching_results.append((package, False))  # 如果包不存在于共享包目录中，记录虚拟环境匹配结果为False
        install_results.append((package, False))  # 记录安装结果为False

# 打印统计信息
print("\n统计信息:")
print(f"总共检查的包数量: {total_packages}")
print(f"共享包目录匹配数: {sharedpackage_matches} 需下载数: {proposed_downloads} 实际下载数: {actual_downloads}")
print(f".venv环境匹配数: {venv_matches} 需安装数: {proposed_installs} 实际安装数: {actual_installs}")

# 提示用户是否打印详细信息
show_details = input("是否打印详细信息？输入Y打印，其他键结束流程: ")

if show_details.lower() == 'y':  # 如果用户输入Y，打印详细信息
    # 打印共享包目录匹配结论
    print("\n共享包目录匹配结论:")
    for package, result in sharedpackage_matching_results:
        print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

    # 打印下载结论
    print("\n下载结论:")
    for package, result in sharedpackage_download_results:
        print(f"包 '{package}' 下载结果: {'成功' if result == True else '无需下载' if result == '无需下载' else '失败'}")

    # 打印.venv环境匹配结论
    print("\n.venv环境匹配结论:")
    for package, result in venv_matching_results:
        print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

    # 打印安装结论
    print("\n安装结论:")
    for package, result in install_results:
        print(f"包 '{package}' 安装结果: {'成功' if result == True else '无需安装' if result == '无需安装' else '失败'}")

    # 提示用户是否打印匹配详细信息
    show_match_details = input("是否打印匹配详细信息？输入Y打印，其他键结束流程: ")

    if show_match_details.lower() == 'y':  # 如果用户输入Y，打印匹配详细信息
        print("\n共享包匹配明细:")
        for package_name, file, matched in sharedpackage_match_details:
            print(f"检查包是否存在: {package_name}，匹配{'成功' if matched else '失败'}: {file}")

        print("\n.venv匹配明细:")
        for package_name, installed_package, matched in venv_match_details:
            print(f"检查包是否存在: {package_name}，匹配{'成功' if matched else '失败'}: {installed_package}")
else:
    print("流程结束。")
