import os
import configparser
import shutil
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

# 日志函数
def log_error(message):
    if LOG_PATH.is_dir():
        log_file = LOG_PATH / "create_links.log"
    else:
        log_file = LOG_PATH

    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - ERROR - {message}\n")
    print(f"ERROR: {message}")  # 输出错误到终端

def log_info(message):
    if LOG_PATH.is_dir():
        log_file = LOG_PATH / "create_links.log"
    else:
        log_file = LOG_PATH

    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - INFO - {message}\n")
    print(f"INFO: {message}")   # 输出信息到终端

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 检查配置文件是否存在必要的配置项
required_sections = ["Paths", "FileTypes", "Settings"]
for section in required_sections:
    if section not in config:
        log_error(f"配置文件中缺少 {section} 部分")
        exit(1)

# 从配置文件获取参数并转为 Path 对象
SOURCE_DIR = Path(config.get('Paths', 'SOURCE_DIR', fallback=''))
DEST_DIR = Path(config.get('Paths', 'DEST_DIR', fallback=''))
LOG_PATH = Path(config.get('Paths', 'LOG_PATH', fallback='./log.txt'))

link_type_set = set(ftype.lower() for ftype in config.get('FileTypes', 'link_types').split(','))
copy_type_set = set(ftype.lower() for ftype in config.get('FileTypes', 'copy_types').split(','))

MAX_THREADS = config.getint('Settings', 'MAX_THREADS', fallback=10)

#数据统计
link_count = 0
copy_count = 0
exist_count = 0
error_count = 0

# 创建一个线程锁
counter_lock = threading.Lock()

def create_links(source_filepath: Path, dest_filepath: Path):
    global link_count, copy_count, exist_count, error_count
    
    try:
        file_ext = source_filepath.suffix.lower()

        if file_ext in link_type_set:
            os.symlink(source_filepath, dest_filepath)
            log_info(f"{source_filepath} 创建软链完成")
            with counter_lock:
                link_count += 1

        elif file_ext in copy_type_set:
            shutil.copy(source_filepath, dest_filepath)
            log_info(f"{source_filepath} 复制完成")
            with counter_lock:
                copy_count += 1
            
    except FileExistsError:
        log_info(f"{dest_filepath} 已存在")
        with counter_lock:
            exist_count += 1
    except Exception as e:
        log_error(f"处理 {source_filepath} 时出错: {str(e)}")
        with counter_lock:
            error_count += 1

def main():
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for root, _, files in os.walk(SOURCE_DIR):
            for name in files:
                source_filepath = Path(root) / name
                relative_path = source_filepath.relative_to(SOURCE_DIR)
                dest_filepath = DEST_DIR / relative_path
                dest_filepath.parent.mkdir(parents=True, exist_ok=True)

                executor.submit(create_links, source_filepath, dest_filepath)

    print("\n统计数据:")
    print(f"成功创建的软链接数量: {link_count}")
    print(f"成功复制的文件数量: {copy_count}")
    print(f"已存在的文件或软链接数量: {exist_count}")
    print(f"遇到的错误数量: {error_count}")
    print("Successfully completed")

if __name__ == "__main__":
    main()