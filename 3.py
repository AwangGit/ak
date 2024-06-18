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
    installed_packages = pkg_resources.working_set
    installed_package_names = [pkg.key for pkg in installed_packages]
    return package_name.lower().replace('-', '_') in installed_package_names


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

for package in packages:
    sharedpackage_exists = package_exists(package, existing_files)
    sharedpackage_matching_results.append((package, sharedpackage_exists))

    if not sharedpackage_exists:
        print(f"包 '{package}' 不存在于目标目录中，开始下载...")
        download_success = download_package(package, target_dir)
        sharedpackage_download_results.append((package, download_success))
        if download_success:
            sharedpackage_exists = package_exists(package, os.listdir(target_dir))

    if sharedpackage_exists:
        venv_exists = venv_package_exists(package)
        venv_matching_results.append((package, venv_exists))
        if not venv_exists:
            print(f"包 '{package}' 不存在于.venv环境中，从共享目录安装...")
            install_success = install_package_from_directory(package, target_dir)
            install_results.append((package, install_success))
        else:
            install_results.append((package, "无需安装"))
    else:
        sharedpackage_download_results.append((package, False))
        venv_matching_results.append((package, False))
        install_results.append((package, False))

# 打印匹配结论
print("\n共享包目录匹配结论:")
for package, result in sharedpackage_matching_results:
    print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

# 打印下载结论
print("\n下载结论:")
for package, result in sharedpackage_download_results:
    print(f"包 '{package}' 下载结果: {'成功' if result else '失败'}")

# 打印.venv环境匹配结论
print("\n.venv环境匹配结论:")
for package, result in venv_matching_results:
    print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

# 打印安装结论
print("\n安装结论:")
for package, result in install_results:
    print(f"包 '{package}' 安装结果: {result}")
