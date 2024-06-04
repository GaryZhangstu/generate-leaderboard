import subprocess

def run_script():
    # 定义要运行的命令及参数
    command = [
        'python', 'elo_analysis.py',
        '--category', 'chinese', 'english', 'full',
        '--rating-system', 'elo',
        '--clean-battle-file', '.\\clean_battle_20240531.json'
    ]

    # 运行命令并捕获输出
    result = subprocess.run(command, capture_output=True, text=True)

    # 输出命令结果
    print('stdout:', result.stdout)
    print('stderr:', result.stderr)

# 调用方法
run_script()
