import pyvisa as visa
import numpy as np


class YOKOSA:
    def __init__(self, res='TCPIP0::192.168.1.35::8000::SOCKET', quiet=True):
        """
        初始化YOKOGAWA光谱仪连接

        参数:
            res (str): VISA资源字符串，格式为'TCPIP0::<IP>::<PORT>::SOCKET'
            quiet (bool): 是否静默模式(减少输出)
        """
        self.quiet = quiet
        self.rm = visa.ResourceManager()

        if not self.quiet:
            print("可用资源:", self.rm.list_resources())

        try:
            # 打开设备连接
            self.dev = self.rm.open_resource(res)
            self.dev.read_termination = '\r\n'  # 设置读取终止符
            self.dev.write_termination = '\n'  # 设置写入终止符
            self.dev.timeout = 20000  # 设置超时时间(毫秒)

            # 尝试打开匿名连接
            try:
                response = self.dev.query('OPEN "anonymous"')
                if not self.quiet:
                    print(f"OPEN响应: {response}")
            except visa.errors.VisaIOError as e:
                if not self.quiet:
                    print("首次OPEN查询失败，可能需要将仪器切换回本地模式")
                    print(f"错误详情: {e}")

            # 查询格式
            format_response = self.dev.query(':FORM?')
            if not self.quiet:
                print(f"格式响应: {format_response}")

            # 查询设备ID
            self.idn = self.dev.query('*IDN?')
            if not self.quiet:
                print(f"设备ID: {self.idn}")

        except Exception as e:
            print(f"初始化失败: {e}")
            raise

    def __del__(self):
        """析构函数，确保连接关闭"""
        if hasattr(self, 'dev'):
            self.dev.close()

    def get_idn(self):
        """获取设备标识信息"""
        return self.idn if hasattr(self, 'idn') else None


if __name__ == '__main__':
    # 测试示例
    try:
        # 替换为你的实际IP和端口
        res = 'TCPIP0::192.168.1.35::8000::SOCKET'
        osa = YOKOSA(res=res, quiet=False)

        # 打印设备ID
        print("\n设备标识信息:", osa.get_idn())

    except Exception as e:
        print(f"测试失败: {e}")