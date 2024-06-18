import os
import re
import subprocess
import sys
import pkg_resources

# 定义目标目录和requirements文件路径
target_dir = "D:\\Project\\Shared_packages"
requirements_file = "requirements.txt"

# 读取requirements文件并获取包列表
with open(requirements_file, "r") as file:
    packages = [line.strip() for line in file if line.strip()]

# 打印从requirements文件中读取的包名
print("从requirements文件中读取的包名:")
for package in packages:
    print(package)

# 获取目标目录中的现有文件
existing_files = os.listdir(target_dir)

# 打印从目标目录中读取的文件名
print("\n从目标目录中读取的文件名:")
for file in existing_files:
    print(file)


# 函数：检查包是否存在
def package_exists(package_name, file_list):
    # 使用正则表达式检查包名，忽略版本号和文件扩展名
    normalized_package_name = package_name.replace('-', '_').lower()
    pattern = re.compile(rf'{re.escape(normalized_package_name)}(-\d+(\.\d+)*.*)?(\.whl|\.tar\.gz|\.zip)?',
                         re.IGNORECASE)

    print(f"\n检查包是否存在: {package_name}")
    for file in file_list:
        normalized_file_name = file.replace('-', '_').lower()
        match = pattern.match(normalized_file_name)
        if match:
            print(f"检查包是否存在: {package_name}，匹配成功: {file}")
            return True
        else:
            print(f"检查包是否存在: {package_name}，匹配失败: {file}")
    return False


# 检查.venv环境中的包
def venv_package_exists(package_name):
    normalized_package_name = package_name.replace('-', '_').lower()
    installed_packages = pkg_resources.working_set
    installed_package_names = [pkg.key.lower().replace('-', '_') for pkg in installed_packages]
    return normalized_package_name in installed_package_names


# 下载包并安装
def download_package(package_name, target_directory):
    download_success = False
    # 下载包
    result = subprocess.run([sys.executable, '-m', 'pip', 'download', package_name, '-d', target_directory])
    if result.returncode == 0:
        download_success = True
    return download_success


def install_package_from_directory(package_name, target_directory):
    install_success = False
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--no-index', '--find-links', target_directory, package_name])
    if result.returncode == 0:
        install_success = True
    return install_success


# 检查包名匹配情况并安装包
print("\n包名匹配情况:")
sharedpackage_matching_results = []
sharedpackage_download_results = []
venv_matching_results = []
install_results = []

total_packages = len(packages)
proposed_downloads = 0
actual_downloads = 0
proposed_installs = 0
actual_installs = 0

for package in packages:
    sharedpackage_exists = package_exists(package, existing_files)
    sharedpackage_matching_results.append((package, sharedpackage_exists))

    if not sharedpackage_exists:
        proposed_downloads += 1
        print(f"包 '{package}' 不存在于目标目录中，开始下载...")
        download_success = download_package(package, target_dir)
        sharedpackage_download_results.append((package, download_success))
        if download_success:
            actual_downloads += 1
            sharedpackage_exists = package_exists(package, os.listdir(target_dir))
    else:
        sharedpackage_download_results.append((package, "无需下载"))

    if sharedpackage_exists:
        venv_exists = venv_package_exists(package)
        venv_matching_results.append((package, venv_exists))
        if not venv_exists:
            proposed_installs += 1
            print(f"包 '{package}' 不存在于.venv环境中，从共享目录安装...")
            install_success = install_package_from_directory(package, target_dir)
            install_results.append((package, install_success))
            if install_success:
                actual_installs += 1
        else:
            install_results.append((package, "无需安装"))
    else:
        venv_matching_results.append((package, False))
        install_results.append((package, False))

# 打印匹配结论
print("\n共享包目录匹配结论:")
for package, result in sharedpackage_matching_results:
    print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

# 打印下载结论
print("\n下载结论:")
for package, result in sharedpackage_download_results:
    print(f"包 '{package}' 下载结果: {'成功' if result else '无需下载' if result == '无需下载' else '失败'}")

# 打印.venv环境匹配结论
print("\n.venv环境匹配结论:")
for package, result in venv_matching_results:
    print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

# 打印安装结论
print("\n安装结论:")
for package, result in install_results:
    print(f"包 '{package}' 安装结果: {result}")

# 打印统计信息
print("\n统计信息:")
print(f"总共检查的包数量: {total_packages}")
print(f"拟下载包的数量: {proposed_downloads}")
print(f"最终下载包的数量: {actual_downloads}")
print(f"拟安装包的数量: {proposed_installs}")
print(f"最终安装包的数量: {actual_installs}")
