# 示例：Python 代码 → 翻译为其他语言

def fibonacci(n: int) -> int:
    """计算第 n 个斐波那契数"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def main():
    for i in range(10):
        print(f"fib({i}) = {fibonacci(i)}")


if __name__ == "__main__":
    main()
