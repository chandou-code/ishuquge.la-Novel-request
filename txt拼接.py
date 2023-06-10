import os
import datetime

# 获取当前文件夹内的所有文件名
files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]

# 获取每个文件的最后修改时间，并将它们存放到一个元组中
file_times = [(f, datetime.datetime.fromtimestamp(os.path.getmtime(f))) for f in files]

# 根据最后修改时间对元组进行排序，并从排序后的元组中获取文件名
sorted_files = [f[0] for f in sorted(file_times, key=lambda x: x[1])]

# # 输出排序后的文件名列表
# print(sorted_files)

# 创建新txt文件的文件名
new_file_name = "new_file.txt"

# 打开新txt文件，'a'参数表示以追加模式打开文件
with open(new_file_name, 'a',encoding='utf-8') as new_file:
	# 遍历列表中每个txt文件名
	for txt_file_title in sorted_files:
		# 打开对应的txt文件
		with open(txt_file_title, 'r',encoding='utf-8') as txt_file:
			# 读取txt文件内容并追加到新的txt文件中
			content = txt_file.read()
			new_file.write(content + '\n') # 每个txt文件内容之间换行

# 关闭文件
new_file.close()

