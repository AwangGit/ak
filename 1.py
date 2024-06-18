import os
import re
import subprocess

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


# 下载包并安装
def download_and_install_package(package_name, target_directory):
    download_success = False
    install_success = False

    # 下载包
    result = subprocess.run(['pip', 'download', package_name, '-d', target_directory])
    if result.returncode == 0:
        download_success = True

    # 重新获取目标目录中的现有文件
    existing_files = os.listdir(target_directory)

    # 检查包是否存在
    if package_exists(package_name, existing_files):
        # 安装包
        result = subprocess.run(['pip', 'install', '--no-index', '--find-links', target_directory, package_name])
        if result.returncode == 0:
            install_success = True
    else:
        print(f"包 '{package_name}' 下载失败，无法安装。")

    return download_success, install_success


# 检查包名匹配情况并安装包
print("\n包名匹配情况:")
matching_results = []
download_results = []
install_results = []

for package in packages:
    exists = package_exists(package, existing_files)
    matching_results.append((package, exists))
    if exists:
        print(f"包 '{package}' 已存在于目标目录中，直接安装...")
        result = subprocess.run(['pip', 'install', '--no-index', '--find-links', target_dir, package])
        install_success = (result.returncode == 0)
        install_results.append((package, install_success))
    else:
        print(f"包 '{package}' 不存在于目标目录中，开始下载并安装...")
        download_success, install_success = download_and_install_package(package, target_dir)
        download_results.append((package, download_success))
        install_results.append((package, install_success))

# 打印匹配结论
print("\n匹配结论:")
for package, result in matching_results:
    print(f"包 '{package}' 匹配结果: {'存在' if result else '不存在'}")

# 打印下载结论
print("\n下载结论:")
for package, result in download_results:
    print(f"包 '{package}' 下载结果: {'成功' if result else '失败'}")

# 打印安装结论
print("\n安装结论:")
for package, result in install_results:
    print(f"包 '{package}' 安装结果: {'成功' if result else '失败'}")
