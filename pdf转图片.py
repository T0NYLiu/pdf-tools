import fitz
import os
import json

def pdf2img(pdf_path, img_dir):
    try:
        doc = fitz.open(pdf_path)  # 尝试打开pdf文件
    except Exception as e:
        print(f"Failed to open file {pdf_path}: {e}")
        return False  # 返回False表示处理失败

    base_name = os.path.basename(pdf_path).replace(".pdf", "")  # 获取pdf文件名（不含扩展名）
    for page in doc:  # 遍历pdf的每一页
        zoom_x = 1.0  # 设置每页的水平缩放因子
        zoom_y = 1.0  # 设置每页的垂直缩放因子
        mat = fitz.Matrix(zoom_x, zoom_y)  # 创建缩放矩阵
        pix = page.get_pixmap(matrix=mat)  # 获取页面的位图对象
        output_path = os.path.join(img_dir, f"{base_name}-page{page.number + 1}.png")  # 生成图片保存路径
        pix.save(output_path)  # 保存图片到指定目录

    return True  # 返回True表示处理成功

# 创建一个空的文件列表
files = list()

def dirAll(pathname):
    if os.path.exists(pathname):  # 检查路径是否存在
        filelist = os.listdir(pathname)  # 列出路径下的所有文件和文件夹
        for f in filelist:
            f = os.path.join(pathname, f)  # 获取完整路径
            if os.path.isdir(f):  # 如果是文件夹，递归调用
                dirAll(f)
            else:
                files.append(f)  # 将文件路径添加到文件列表中

# 读取已处理的文件记录
record_file = "processed_files.json"
if os.path.exists(record_file):
    with open(record_file, "r", encoding="utf-8") as f:
        processed_files = json.load(f)
else:
    processed_files = []

# 遍历目录并处理所有PDF文件
dirAll(r"/data/zhaoshuofeng/workplace/hongan_data/研报")

# 指定统一的图片保存目录
img_dir = r"/data/zhaoshuofeng/workplace/hongan_data/研报/all_img"
os.makedirs(img_dir, exist_ok=True)  # 确保目录存在

for filepath in files:
    if filepath.lower().endswith(".pdf") and filepath not in processed_files:  # 检查文件是否为PDF文件并且未处理过
        pdf_path = filepath
        print(f"Processing {filepath}")
        try:
            if pdf2img(pdf_path, img_dir):  # 将PDF转换为图片
                processed_files.append(filepath)  # 记录已处理的文件
                # 更新记录文件
                with open(record_file, "w", encoding="utf-8") as f:
                    json.dump(processed_files, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Failed to process {filepath}: {e}")
