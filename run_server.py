from waitress import serve
# 下面这行很重要：假设你的项目文件夹叫 myproject
# 请把 'myproject.wsgi' 中的 'myproject' 换成你实际上包含 settings.py 的那个文件夹名字
from myweb2.wsgi import application 

if __name__ == '__main__':
    print("正在启动抗菌肽数据库后端服务 (端口 8000)...")
    # 允许本机 Nginx 转发过来的请求
    serve(application, host='127.0.0.1', port=8000)